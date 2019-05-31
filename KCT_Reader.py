__author__ = 'zweiss'

# Can convert the format of the KCT corpus and the H1 corpus, but not the H2 corpus

import sys
import re
import os


def rewrite_all_files(input_dir, output_src, output_trgt, meta_file, save_txt):
    """
    Recuryively rewrites all files
    :param input_dir:
    :param output_src:
    :param output_trgt:
    :return:
    """
    error_meta = "filename;n_named_entities;num_foreign;num_g_error;num_incorrect_hyphen;num_incorrect_split;num_known_deletion;num_missing_hyphen;num_missing_split;num_split_at_line_no_hyphen;num_unknown_deletion;num_unreadable;num_word_insertion;num_word_substitution"

    # get a listing of all plain txt files in the dir and all sub dirs
    txt_file_list = []
    for root, dirs, files in os.walk(input_dir):
        for name in files:
            if name.endswith('.txt'):
                txt_file_list.append(os.path.join(root, name))

    relevant_keys = ['alter', 'geschlecht', 'l1', 'schule', 'klassenstufe', 'klasse', 'erhebdatumtag', 'erhebdatummonat', 'num_g_error', 'num_foreign']

    # process all files and save them to the output file
    counter = 0
    for txt_file in txt_file_list:
        print('Started rewriting of ' + txt_file)
        error_meta += "\n"+rewrite_file(txt_file, output_src, output_trgt, relevant_keys, save_txt)
        counter += 1

    with open(meta_file, "w") as outstr:
        outstr.write(error_meta)

    print(str(counter) + ' file(s) rewritten.')


def rewrite_file(txt_file, output_src, output_trgt, relevant_keys, save_txt):
    """
    Rewrites a file
    :param txt_file:
    :param output_src:
    :param output_trgt:
    :param relevant_keys:
    :return:
    """

    # read data
    src_dict, trgt_dict, meta_dict = read_kct(txt_file)

    # get plain texts
    src_text, num_f, num_g, num_unreadable, num_missing_split, num_incorrect_split , num_missing_hyphen , num_incorrect_hyphen, num_split_at_line_no_hyphen , num_unknown_deletion , num_known_deletion , n_named_entities , num_word_insertion , num_word_substitution = get_plain_text_in_order(src_dict)
    trgt_text, _, _, _, _, _, _, _, _, _, _, _, _, _ = get_plain_text_in_order(trgt_dict)

    # add final meta information
    meta_dict['num_g_error'] = str(num_g)
    meta_dict['num_foreign'] = str(num_f)

    meta_dict['num_unreadable'] = str(num_unreadable)
    meta_dict['num_missing_split'] = str(num_missing_split)
    meta_dict['num_incorrect_split'] = str(num_incorrect_split)
    meta_dict['num_missing_hyphen'] = str(num_missing_hyphen)
    meta_dict['num_incorrect_hyphen'] = str(num_incorrect_hyphen)
    meta_dict['num_split_at_line_no_hyphen'] = str(num_split_at_line_no_hyphen)
    meta_dict['num_unknown_deletion'] = str(num_unknown_deletion)
    meta_dict['num_known_deletion'] = str(num_known_deletion)
    meta_dict['n_named_entities'] = str(n_named_entities)
    meta_dict['num_word_substitution'] = str(num_word_substitution)
    meta_dict['num_word_insertion'] = str(num_word_insertion)

    # write to output files
    prefix = get_file_name(txt_file[txt_file.rfind('/')+1:], meta_dict, relevant_keys)

    rval = prefix+".txt"
    for key in ["n_named_entities","num_foreign","num_g_error","num_incorrect_hyphen","num_incorrect_split","num_known_deletion","num_missing_hyphen","num_missing_split","num_split_at_line_no_hyphen","num_unknown_deletion","num_unreadable","num_word_insertion","num_word_substitution"]:
        rval += ";"+meta_dict[key]

    if save_txt:
        src_file = output_src + 'original-' + prefix + '.txt'
        src_writer = open(src_file, 'w')
        src_writer.write(src_text)
        src_writer.close()
        #print('Wrote source to ' + src_file)

        trgt_file = output_trgt + 'corrected-' + prefix + '.txt'
        trgt_writer = open(trgt_file, 'w')
        trgt_writer.write(trgt_text)
        trgt_writer.close()
        #print('Wrote target to ' + trgt_file)
    return rval


def read_kct(file):
    """
    Reads text from the Karlsruhe Children Texts Corpus. Separates them into actual text written by the children,
    corrected versions of these texts, and meta information on a text.
    :param file:
    :return: triple: dictionary of
    """
    reader = open(file, 'r')

    achieved_text = {}
    target_text = {}
    meta_info = {}
    for l in reader.readlines():
        line = l.strip()

        # meta information
        if line.startswith('\\\\') and not line.endswith('-end\n'):
            # achieved text
            if line.startswith('\\\\Kind'):
                key = int(line[len('\\\\Kind'):].split('-')[0])   # get sentence id located between prefix and hypen
                text_type = 1
            # corrected text
            elif line.startswith('\\\\Richtig'):
                key = int(line[len('\\\\Richtig'):].split('-')[0])   # get sentence id located between prefix and hypen
                text_type = 0
            # other meta information
            else:
                key = line[len('\\\\'):].split('-')[0].strip()
                text_type = -1

        # actual text
        elif len(line) > 0:
            # achieved text
            if text_type == 1:
                add_or_append_to_dict(achieved_text, key, ' ' + line)
            # target text
            elif text_type == 0:
                add_or_append_to_dict(target_text, key, ' ' + line)
            # meta information
            elif text_type == -1:
                add_or_append_to_dict(meta_info, key, ' ' + line)

    reader.close()
    return achieved_text, target_text, meta_info


def add_or_append_to_dict(dictionary, key, value):
    """
    Helper to add or append a value to a dictionary
    :param dictionary:
    :param key:
    :param value:
    :return:
    """
    if key in dictionary.keys():
        dictionary[key] += value
    else:
        dictionary[key] = value


def get_plain_text_in_order(text_dict, remove_errors = True, auto_correct = True):
    """
    Helper to get plain text version of dictionary in correct order with or without error annotation
    :param text_dict:
    :param remove_errors remove error annotation, default = True
    :param auto_correct inserts empty spaces, if necessary, default = True
    :return: triple of text, number of foreign words, number of grammatical errors
    """
    text = ''
    num_foreign = num_grammar = 0
    num_unreadable = 0
    num_missing_split = 0
    num_incorrect_split = 0
    num_missing_hyphen = 0
    num_incorrect_hyphen = 0
    num_split_at_line_no_hyphen = 0
    num_unknown_deletion = 0
    num_known_deletion = 0
    n_named_entities = 0
    num_word_insertion = 0
    num_word_substitution = 0

    pattern_replace = re.compile("\[[A-Za-zÖÄÜöäüß]+ [A-Za-zÖÄÜöäüß]+\]")

    for key in sorted(text_dict.keys()):
        sentence = text_dict[key]

        # count error types
        num_foreign += sentence.count('{F}')
        num_grammar += sentence.count('{G}')
        n_named_entities += sentence.count('{N}')
        num_unreadable += sentence.count('*')
        num_missing_split += sentence.count('_')
        c_num_word_insertion = sentence.count("§]")
        num_word_insertion += c_num_word_insertion
        c_num_unknown_deletion = sentence.count("[$ fehlendeswort]")
        num_unknown_deletion += c_num_unknown_deletion
        c_num_known_deletion = sentence.count('[§') - c_num_unknown_deletion
        num_known_deletion += c_num_known_deletion
        num_incorrect_split += sentence.count('§') - c_num_unknown_deletion - c_num_known_deletion - c_num_word_insertion
        num_missing_hyphen+= sentence.count('=')
        num_incorrect_hyphen+= sentence.count('~')
        num_split_at_line_no_hyphen += sentence.count("--")

        num_word_substitution += len(pattern_replace.findall(sentence))



        if auto_correct:
            sentence = re.sub('\*|{[1-9A-Z]+}|§|=|~|--|\[.*\]', '', sentence)
            sentence = re.sub('_', ' ', sentence)
            sentence = sentence.replace('&#34;', '\"')

        elif remove_errors:
            sentence = re.sub('\*|{[1-9A-Z]+}|§|=|~|--|\[.*\]|_', '', sentence)

        text += sentence.strip() + '\n'

    return text.strip(), num_foreign, num_grammar, num_unreadable, num_missing_split, num_incorrect_split , num_missing_hyphen , num_incorrect_hyphen, num_split_at_line_no_hyphen , num_unknown_deletion , num_known_deletion , n_named_entities , num_word_insertion , num_word_substitution


def get_file_name(old_file, meta_dict, relevant_keys):
    prefix = old_file[0:old_file.rindex('.')]
    for key in relevant_keys:
        value = 'none'
        if key in meta_dict.keys():
            value = meta_dict[key].strip().lower()
            value = value.replace(' ', '')
            value = re.sub(',|;|\.|!|\?|-', '_', value)
            value = value.replace('ä', 'ae')
            value = value.replace('ö', 'oe')
            value = value.replace('ü', 'ue')
            value = value.replace('ß', 'ss')
            if len(value.strip()) == 0 or value.strip() == '_':
                value = 'none'
        prefix += '-' + value
    return prefix


if __name__ == '__main__':
    """
    Call
    > python3 KCT_Reader.py corpus_directory original_writing_output_directory corrected_writing_output_directory output_file_meta_infos
    """

    in_dir = sys.argv[1]
    src_out = sys.argv[2]
    trgt_out = sys.argv[3]
    meta_File = sys.argv[4]

    in_dir = '/Users/zweiss/Documents/LiteratureARessources/corpora/german-fla/Karlsruhe_Childrens_Text/crosssectional/data/original/'
    src_out = '/Users/zweiss/Documents/LiteratureARessources/corpora/german-fla/Karlsruhe_Childrens_Text/crosssectional/data/tmp2/'
    trgt_out = '/Users/zweiss/Documents/LiteratureARessources/corpora/german-fla/Karlsruhe_Childrens_Text/crosssectional/data/tmp1/'
    meta_File = "/Users/zweiss/Documents/LiteratureARessources/corpora/german-fla/Karlsruhe_Childrens_Text/crosssectional/data/plain_texts+meta/accuracy-meta.csv"

    rewrite_all_files(in_dir, src_out, trgt_out, meta_File, save_txt=False)