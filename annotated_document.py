import os
import re
import numpy as np


class AnnotatedStudentWriting:

    REPLACEMENT_PATTERN = re.compile(r"\[[A-Za-zÖÄÜöäüß]+ [A-Za-zÖÄÜöäüß]+\]")
    ERROR_PATTERN = re.compile(r"\*|{[1-9A-Z]+}|§|=|~|--|_|\[.*\]")
    ERROR_PATTERN1 = re.compile(r"\*|{[1-9A-Z]+}|\[")
    ERROR_PATTERN2 = re.compile(r"\]|§|=|~|--|_|")
    EMPTY_PATTERN = re.compile(r"( )+")

    KCT_META_HEADER = ['alter', 'didkonzept', 'erhebdatummonat', 'erhebdatumtag', 'geschlecht', 'klasse',
                       'klassenstufe', 'l1', 'schreibanlass', 'schule', 'sonstiges', 'transkribpersonname']

    def __init__(self):
        self.file_name = ""
        self.meta_dict = {}
        self.debug = False

        self.original_text = ""
        self.corrected_text = ""

    def __str__(self):
        rval = self.file_name
        rval += (os.linesep*2) + self.original_text
        rval += (os.linesep*2) + self.corrected_text
        rval += (os.linesep*2)
        for key in sorted(self.meta_dict):
            rval += str(key) + ": " + str(self.meta_dict[key]) + os.linesep
        return rval.strip()

    def start_debug_mode(self):
        self.debug = True

    def end_debug_mode(self):
        self.debug = False

    # saving methods

    def save_original(self, out_file, without_annotaions=True):
        if without_annotaions:
            rval = self.print_original_text_without_annotations()
        else:
            rval = self.original_text
        AnnotatedStudentWriting.save(out_file, rval)

    def save_corrected(self, out_file, without_annotaions=True):
        if without_annotaions:
            rval = self.print_corrected_text_without_annotations()
        else:
            rval = self.corrected_text
        AnnotatedStudentWriting.save(out_file, rval)

    def save_meta_information(self, out_file, delim=";", is_new_file=True):
        # get content
        sorted_keys = sorted(self.meta_dict.keys())
        meta_as_string = os.linesep
        for key in sorted_keys:
            meta_as_string += re.sub(os.linesep, " ", re.sub(delim, "", str(self.meta_dict[key]))) + delim
        meta_as_string = meta_as_string[:-1]  # remove last delimiter

        if is_new_file:
            # add header
            meta_as_string = delim.join(sorted_keys) + meta_as_string
            AnnotatedStudentWriting.save(out_file, meta_as_string)
        else:
            with open(out_file, 'a', encoding="utf-8") as outstr:
                outstr.write(meta_as_string)

    @staticmethod
    def save(out_file, content):
        with open(out_file, 'w', encoding="utf-8") as outstr:
            outstr.write(content)

    # reading methods

    def load_kct_file(self, in_file, be_verbose=True):
        self.file_name = in_file[in_file.rfind(os.path.sep)+1:]

        if be_verbose:
            print(in_file)

        achieved_text = {}
        target_text = {}

        with open(in_file, 'r', encoding="utf-8") as instr:
            text_type = "Issue"
            for l in instr.readlines():
                line = str(l.strip())

                # meta information
                if line.startswith('\\') and not line.endswith('-end\n'):
                    # achieved text
                    if "Kind" in line:
                        key = int(line[line.find("Kind")+4:].split('-')[0])  # get sentence id located between prefix and hypen
                        text_type = 1
                    # corrected text
                    elif "Richtig" in line:
                        key = int(line[line.find("Richtig")+7:].split('-')[0])  # get sentence id located between prefix and hypen
                        text_type = 0
                    # other meta information
                    else:
                        key = line[len('\\')+1:].split('-')[0].strip()
                        text_type = -1

                # actual text
                elif len(line) > 0:
                    # achieved text
                    if text_type == 1:
                        AnnotatedStudentWriting.add_or_append_to_dict(achieved_text, key, ' ' + line)
                    # target text
                    elif text_type == 0:
                        AnnotatedStudentWriting.add_or_append_to_dict(target_text, key, ' ' + line)
                    # meta information
                    elif text_type == -1:
                        AnnotatedStudentWriting.add_or_append_to_dict(self.meta_dict, key, line)
                    elif text_type == "Issue":
                        print("Problematic file content. Skipping file: "+in_file)
                        break

        for snum in sorted(achieved_text.keys()):
            self.original_text += achieved_text[snum]
        for snum in sorted(target_text.keys()):
            self.corrected_text += target_text[snum]

        self.original_text = self.original_text.strip()
        self.corrected_text = self.corrected_text.strip()

        self.retrieve_annotation_based_counts()
        self.retrieve_diff_based_counts()
        # add file to meta to identify it later on
        self.meta_dict['file_path'] = in_file[:in_file.rfind(os.path.sep)]
        self.meta_dict['file_name'] = self.file_name

        # check if all required header have been found, otherwise add NA
        for rk in AnnotatedStudentWriting.KCT_META_HEADER:
            if rk not in self.meta_dict.keys():
                self.meta_dict[rk] = "NA"

    def load_h1_or_h2_file(self, in_file, be_verbose=True):
        self.file_name = in_file[in_file.rfind(os.path.sep) + 1:]

        # skip original texts: are processed with target texts
        if be_verbose:
            print(in_file)

        # read corrected text
        with open(in_file, 'r', encoding="utf-8") as instr:
            self.corrected_text = instr.read().strip()
        # infer name of original text from the target text file
        orig_in_file = os.path.join(in_file[:in_file.rfind(os.path.sep)], "a"+self.file_name[1:])
        with open(orig_in_file, 'r', encoding="utf-8") as instr:
            self.original_text = instr.read().strip()

        self.retrieve_annotation_based_counts()
        self.retrieve_diff_based_counts()
        # add file to meta to identify it later on
        self.meta_dict['file_path'] = in_file[:in_file.rfind(os.path.sep)]
        self.meta_dict['file_name'] = self.file_name

    # helper methods

    def print_corrected_text_without_annotations(self):
        rval = re.sub(AnnotatedStudentWriting.ERROR_PATTERN1, '', self.corrected_text)
        rval = re.sub('_', ' ', rval)
        rval = re.sub('=', '-', rval)
        rval = re.sub('~([A-ZÖÄÜ])', r' \1', rval)
        rval = rval .replace('&#34;', '\"')
        rval = re.sub(AnnotatedStudentWriting.ERROR_PATTERN2, '', rval)
        rval = re.sub(AnnotatedStudentWriting.EMPTY_PATTERN, ' ', rval)
        return rval

    def print_original_text_without_annotations(self):
        # remove annotations from original text
        rval = re.sub('\[§.*\]', '', self.original_text)
        rval = re.sub(AnnotatedStudentWriting.ERROR_PATTERN1, '', rval)
        rval = re.sub('_', '', rval)
        rval = re.sub('§', ' ', rval)
        rval = re.sub('~', '-', rval)
        rval = re.sub('--', ' ', rval)
        rval = rval.replace('&#34;', '\"')
        rval = re.sub(AnnotatedStudentWriting.ERROR_PATTERN2, '', rval)
        rval = re.sub(AnnotatedStudentWriting.EMPTY_PATTERN, ' ', rval)
        return rval

    def retrieve_annotation_based_counts(self):
        # count error types
        num_foreign = self.corrected_text.count('{F}')
        num_grammar = self.corrected_text.count('{G}')
        num_named_entities = self.corrected_text.count('{N}')
        num_unreadable = self.corrected_text.count('*')
        num_missing_split = self.corrected_text.count('_')
        c_num_word_insertion = self.corrected_text.count("§]")
        num_word_insertion = c_num_word_insertion
        c_num_unknown_deletion = self.corrected_text.count("[$ fehlendeswort]")
        num_unknown_deletion = c_num_unknown_deletion
        c_num_known_deletion = self.corrected_text.count('[§') - c_num_unknown_deletion
        num_known_deletion = c_num_known_deletion
        num_incorrect_split = self.corrected_text.count(
            '§') - c_num_unknown_deletion - c_num_known_deletion - c_num_word_insertion
        num_missing_hyphen = self.corrected_text.count('=')
        num_incorrect_hyphen = self.corrected_text.count('~')
        num_split_at_line_no_hyphen = self.corrected_text.count("--")
        num_word_substitution = len(AnnotatedStudentWriting.REPLACEMENT_PATTERN.findall(self.corrected_text))
        # add this stuff to meta information
        self.meta_dict['num_g_error'] = str(num_foreign)
        self.meta_dict['num_foreign'] = str(num_grammar)
        self.meta_dict['num_unreadable'] = str(num_unreadable)
        self.meta_dict['num_missing_split'] = str(num_missing_split)
        self.meta_dict['num_incorrect_split'] = str(num_incorrect_split)
        self.meta_dict['num_missing_hyphen'] = str(num_missing_hyphen)
        self.meta_dict['num_incorrect_hyphen'] = str(num_incorrect_hyphen)
        self.meta_dict['num_split_at_line_no_hyphen'] = str(num_split_at_line_no_hyphen)
        self.meta_dict['num_unknown_deletion'] = str(num_unknown_deletion)
        self.meta_dict['num_known_deletion'] = str(num_known_deletion)
        self.meta_dict['num_named_entities'] = str(num_named_entities)
        self.meta_dict['num_word_substitution'] = str(num_word_substitution)
        self.meta_dict['num_word_insertion'] = str(num_word_insertion)

    def retrieve_diff_based_counts(self):
        corrected_split = re.sub(AnnotatedStudentWriting.EMPTY_PATTERN, " ", self.corrected_text).split(" ")
        original_split = re.sub(AnnotatedStudentWriting.EMPTY_PATTERN, " ", self.original_text).split(" ")

        num_missing_punctuation_errors = 0
        num_superfluous_punctuation_errors = 0
        num_incorrect_choice_punctuation_errors = 0
        num_case_errors = 0
        num_missing_quotes_errors = 0
        num_orthographical_errors = 0
        num_superfluous_quotes_errors = 0
        num_unidentified_error = 0

        # sanity check:
        if len(corrected_split) != len(original_split):
            print("Issue with file: " + self.file_name + " : "+str(len(original_split))+" vs. "+str(len(corrected_split)))
            num_missing_punctuation_errors = np.nan
            num_superfluous_punctuation_errors = np.nan
            num_incorrect_choice_punctuation_errors = np.nan
            num_case_errors = np.nan
            num_missing_quotes_errors = np.nan
            num_orthographical_errors = np.nan
            num_superfluous_quotes_errors = np.nan
            num_unidentified_error = np.nan

        else:
            for i, _ in enumerate(original_split):
                corr_tok = re.sub(AnnotatedStudentWriting.ERROR_PATTERN1, '', corrected_split[i])
                corr_tok = re.sub(AnnotatedStudentWriting.ERROR_PATTERN2, '', corr_tok)
                corr_tok = re.sub("&#34;", '\"', corr_tok)
                orig_tok = re.sub(AnnotatedStudentWriting.ERROR_PATTERN1, '', original_split[i])
                orig_tok = re.sub(AnnotatedStudentWriting.ERROR_PATTERN2, '', orig_tok)
                orig_tok = re.sub("&#34;", '\"', orig_tok)
                corr_tok = corr_tok.strip()
                orig_tok = orig_tok.strip()
                if not corr_tok == orig_tok:

                    # missing punctuation error: corrected version has punctuation at end of word, but original not
                    if corr_tok.startswith("\"") or orig_tok.startswith("\"") or corr_tok.endswith("\"") or orig_tok.endswith("\""):
                        if corr_tok.startswith("\"") and not orig_tok.startswith("\""):
                            num_missing_quotes_errors += 1
                            # remove this error for further analysis
                            corr_tok = corr_tok[1:] if len(corr_tok)>0 else corr_tok
                        elif orig_tok.startswith("\"") and not corr_tok.startswith("\""):
                            num_superfluous_quotes_errors += 1
                            # remove this error for further analysis
                            orig_tok = orig_tok[1:] if len(orig_tok)>0 else orig_tok
                        # check if there is a second quotation mark (probably somewhere at the end)
                        if "\"" in corr_tok and not "\"" in orig_tok:
                            num_missing_quotes_errors += 1
                            # remove this error for further analysis
                            corr_tok = corr_tok[:corr_tok.rfind("\"")]+corr_tok[corr_tok.rfind("\"")+1:] if len(corr_tok)>0 else corr_tok
                        elif "\"" in orig_tok and not "\"" in corr_tok:
                            num_superfluous_quotes_errors += 1
                            # remove this error for further analysis
                            orig_tok = orig_tok[:orig_tok.rfind("\"")]+orig_tok[orig_tok.rfind("\"")+1:] if len(orig_tok)>0 else orig_tok
                        # remove quotes even if there was no error in their assignment, so that in the following, the comparison logic works
                        if corr_tok.startswith("\"") and orig_tok.startswith("\""):
                            corr_tok = corr_tok[1:] if len(corr_tok)>0 else corr_tok
                            orig_tok = orig_tok[1:] if len(orig_tok)>0 else orig_tok
                        if "\"" in orig_tok and "\"" in corr_tok:
                            corr_tok = corr_tok[:corr_tok.rfind("\"")]+corr_tok[corr_tok.rfind("\"")+1:] if len(corr_tok)>0 else corr_tok
                            orig_tok = orig_tok[:orig_tok.rfind("\"")]+orig_tok[orig_tok.rfind("\"")+1:] if len(orig_tok)>0 else orig_tok

                    if len(corr_tok)>0 and AnnotatedStudentWriting.is_punctuation(corr_tok[-1]) and (len(orig_tok) == 0 or not AnnotatedStudentWriting.is_punctuation(orig_tok[-1])):
                        num_missing_punctuation_errors += 1
                        # remove this error for further analysis
                        corr_tok = corr_tok[:-1]
                    # superfluous punctuation error: original version has punctuation at end of word, but corrected version not
                    elif len(orig_tok)>0 and AnnotatedStudentWriting.is_punctuation(orig_tok[-1]) and (len(corr_tok) == 0 or not AnnotatedStudentWriting.is_punctuation(corr_tok[-1])):
                        num_superfluous_punctuation_errors += 1
                        # remove this error for further analysis
                        orig_tok = orig_tok[:-1]
                    # incorrect punctuation choice error: both versions have punctuation but not the same
                    elif len(corr_tok)>0 and len(orig_tok)>0 and AnnotatedStudentWriting.is_punctuation(orig_tok[-1]) and AnnotatedStudentWriting.is_punctuation(corr_tok[-1]) and not orig_tok[-1] == corr_tok[-1]:
                        num_incorrect_choice_punctuation_errors += 1
                        # remove this error for further analysis
                        corr_tok = corr_tok[:-1]
                        orig_tok = orig_tok[:-1]

                    # case error: first letter is identical between corrected and original, but only if both are put to lower case
                    if (len(corr_tok)>0 and len(orig_tok)>0) and (corr_tok[0].lower() == orig_tok[0].lower()) and (corr_tok[0] != orig_tok[0]):
                        num_case_errors += 1
                        # remove this error for further analysis
                        corr_tok = corr_tok[1:]
                        orig_tok = orig_tok[1:]
                    # orthopraphic error: all other deviations
                    if re.sub(r'\W+', '', corr_tok) != re.sub(r'\W+', '', orig_tok):
                        if self.debug:
                            print(orig_tok+" :: "+corr_tok)
                        num_orthographical_errors += 1
                    # something was off, but we don't know what
                    elif corr_tok != orig_tok:
                        if self.debug:
                            print(orig_tok + " ?? " + corr_tok)
                        num_unidentified_error += 1

        self.meta_dict['num_missing_punctuation_errors'] = num_missing_punctuation_errors
        self.meta_dict['num_superfluous_punctuation_errors'] = num_superfluous_punctuation_errors
        self.meta_dict['num_incorrect_choice_punctuation_errors'] = num_incorrect_choice_punctuation_errors
        self.meta_dict['num_upper_lower_case_errors'] = num_case_errors
        self.meta_dict['num_orthographical_errors'] = num_orthographical_errors
        self.meta_dict['num_missing_quotes_errors'] = num_missing_quotes_errors
        self.meta_dict['num_superfluous_quotes_errors'] = num_superfluous_quotes_errors
        self.meta_dict['num_unidentified_error'] = num_unidentified_error

    @staticmethod
    def is_punctuation(acharacter):
        return acharacter == "." or acharacter == "?" or acharacter == "!" or acharacter == ";" or acharacter == "," or acharacter == ":"

    @staticmethod
    def add_or_append_to_dict(cur_dictionary, key, value):
        if key in cur_dictionary.keys():
            cur_dictionary[key] += value
        else:
            cur_dictionary[key] = value

    @staticmethod
    def rec_load_files(input_dir, skip_a_files=True,  file_ending=".txt"):
        file_list = []

        for root, dirs, files in os.walk(input_dir):
            for name in files:
                if not name.startswith(".") and name.endswith(file_ending):
                    if skip_a_files and name.startswith("a_"):
                        continue
                    file_list.append(os.path.join(root, name))
        return file_list


if __name__ == '__main__':

    a = AnnotatedStudentWriting()
    a.start_debug_mode()
    a.load_h1_or_h2_file('/Users/zweiss/Documents/LiteratureARessources/corpora/german-fla/Berkling_Corpora/H1/data/original/Transcriptions/week11/H1.KB.G3/t_H1.KB.G3.8.week11.csv')
    print(a)
    a.save_corrected("test/t_H1.KB.G3.8.week11.txt", True)
    a.save_original("test/a_H1.KB.G3.8.week11", True)
    a.save_meta_information("test/meta-h1.csv", delim=",", is_new_file=True)

    b = AnnotatedStudentWriting()
    b.load_kct_file("/Users/zweiss/Documents/LiteratureARessources/corpora/german-fla/Berkling_Corpora/Karlsruhe_Childrens_Texts/data/original/5_0320/5_0320.txt")

    corrected_split = re.sub(AnnotatedStudentWriting.EMPTY_PATTERN, " ", b.corrected_text).split(" ")
    original_split = re.sub(AnnotatedStudentWriting.EMPTY_PATTERN, " ", b.original_text).split(" ")
    for i, ctok in enumerate(original_split):
        print(ctok+" "+corrected_split[i])



    print(b)
    b.save_corrected("test/4_0012-corrected-unannotated.txt", True)
    b.save_corrected("test/4_0012-corrected-annotated.txt", False)
    b.save_original("test/4_0012-original-unannotated.txt", True)
    b.save_original("test/4_0012-original-annotated.txt", False)
    b.save_meta_information("test/meta.csv", delim=",", is_new_file=False)

