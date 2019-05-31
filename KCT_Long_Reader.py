__author__ = 'zweiss'


import sys
import re
import os


def rewrite_all_files(input_dir, output_src, output_trgt, meta_file):
    """
    Recuryively rewrites all files
    :param input_dir:
    :param output_src:
    :param output_trgt:
    :param meta_file:
    :return:
    """

    # get a listing of all plain txt files in the dir and all sub dirs
    achieved_text_list = []
    target_text_list = []
    for root, dirs, files in os.walk(input_dir):
        for name in files:
            if name.endswith('.csv'):
                if name.startswith('t_H1'):
                    target_text_list.append(os.path.join(root, name))
                elif name.startswith('a_H1'):
                    achieved_text_list.append(os.path.join(root, name))

    meta_dict = get_meta_data(meta_file)

    # process all files and save them to the output file
    counter = 0
    for txt_file in achieved_text_list:
        print('Started rewriting of ' + txt_file)
        rewrite_file(txt_file, output_src, meta_dict, True)
        counter += 1
    for txt_file in target_text_list:
        print('Started rewriting of ' + txt_file)
        rewrite_file(txt_file, output_trgt, meta_dict, False)
        counter += 1

    print(str(counter) + ' file(s) rewritten.')


def get_meta_data(meta_file):
    """
    Reads meta data from csv
    :param meta_file:
    :return:
    """
    meta_dict = {}
    in_stream = open(meta_file, 'r')
    is_header = True
    for line in in_stream.readlines():
        if is_header:
            is_header = False
            continue
        col = line.split(';')
        if len(col) < 16:
            print("Warning: not enough rows: " + str(col))
            continue
        if col[1].strip() in meta_dict.keys():
            print("Warning: redundante rows for id " + col[1].strip())
        else:
            grade = col[2].strip()
            grade_level = col[2][:-1].strip()
            tmp = col[3].strip().lower()
            gender = 'f' if tmp == 'w' else tmp.strip()
            tmp = col[4].split('.')
            month = tmp[0].strip()
            year = tmp[1].strip() if len(tmp) > 1 else ''
            age = col[5].strip()
            school_type = col[6].strip()
            tmp = col[7].strip().lower()[:3]
            l1 = 'deu' if tmp == 'd' else tmp
            tmp = col[8].strip().lower()[:3]
            l2 = 'deu' if tmp == 'd' else tmp
            tmp = col[9].strip().lower()[:3]
            l3 = 'deu' if tmp == 'd' else tmp
            is_multiling = '0' if col[11].strip() == '1' else col[10].strip()
            years_in_germany = col[12].strip()
            book1 = col[13].strip()
            book2 = col[14].strip()
            book3 = col[15][:-1] if col[15].endswith('\n') else col[15]

            meta_dict[col[1].strip()] = [grade, grade_level, gender, month, year, age, school_type, l1, l2, l3,
                                         is_multiling, years_in_germany, book1, book2, book3]
    in_stream.close()
    return meta_dict


def rewrite_file(txt_file, out_dir, meta_dict, is_achieved_text):
    """
    Rewrites a file
    :param txt_file:
    :param out_dir:
    :param meta_dict:
    :param is_achieved_text:
    :return:
    """

    # get data
    text = get_text_from_file(txt_file, is_achieved_text)

    # write it to output file
    name = get_file_name(txt_file[txt_file.rfind('/')+1:], meta_dict)

    src_file = out_dir + ('original-' if is_achieved_text else 'corrected-') + name + '.txt'
    src_writer = open(src_file, 'w')
    src_writer.write(text)
    src_writer.close()


def get_text_from_file(txt_file, is_achieved_text):
    """
    Reads text from the Karlsruhe Children Texts Corpus as either achieved or corrected text
    :param txt_file:
    :param is_achieved_text:
    :return:
    """
    rval = ''
    in_stream = open(txt_file, 'r')
    for l in in_stream.readlines():
        line = l.strip()
        if len(line) == 0:
            continue
        # replace all constructions [dipl norm] with either dipl or norm
        matches = re.findall('\[([^\]]+)\]', line)
        tmp = line
        for m in matches:
            if is_achieved_text:
                tmp = tmp.replace(m, m.split(' ')[0])
                tmp = re.sub('\*|{[1-9A-Z]+}|\[|\]|=|~|--|\[.*\]|_', '', tmp)
                tmp = tmp.replace('§', ' ')
            else:
                tmp = tmp.replace(m, m.split(' ')[1])
                tmp = re.sub('\*|{[1-9A-Z]+}|\[|\]|§|=|~|--|\[.*\]', '', tmp)
                tmp = re.sub('_', ' ', tmp)
                tmp = tmp.replace('&#34;', '\"')
                tmp = re.sub('[a-z]+([A-Z])', ' ', tmp)
        tmp = tmp.replace('  ', ' ')
        rval += tmp.strip() + '\n'
    in_stream.close()
    return rval


def get_file_name(old_file, meta_dict):
    prefix = old_file[0:old_file.rindex('.')]
    student_id = prefix[2:prefix.rindex('.')]

    if student_id not in meta_dict.keys():
        print('Warning: Unknown student id: ' + student_id)
        return prefix + '-none'*17


    week = prefix.split('.')[4]
    week = week.replace('week', '')
    prefix += '-' + student_id + '-' + week

    for info in meta_dict[student_id]:
        value = info.strip().lower()
        value = value.replace(' ', '')
        value = re.sub(',|;|\.|!|\?|-', '_', value)
        value = value.replace('ä', 'ae')
        value = value.replace('ö', 'oe')
        value = value.replace('ü', 'ue')
        value = value.replace('ß', 'ss')

        if len(value.strip()) == 0 or value.strip() == '_' or value.strip() == 'n.a.':
            value = 'none'

        prefix += '-' + value
    return prefix


if __name__ == '__main__':
    """
    Call
    > python3 KCT_Long_Reader.py corpus_directory original_writing_output_directory corrected_writing_output_directory meta_file
    """

    input_dir = sys.argv[1]
    output_src = sys.argv[2]
    output_trgt = sys.argv[3]
    meta_file = sys.argv[4]

    # input_dir = '/Users/zweiss/Documents/0_corpora/Karlsruhe_Childrens_Text/longitudinal/data/original/Transcriptions/'
    # output_src = '/Users/zweiss/Documents/0_corpora/Karlsruhe_Childrens_Text/longitudinal/data/plain_texts+meta/plain_original/'
    # output_trgt = '/Users/zweiss/Documents/0_corpora/Karlsruhe_Childrens_Text/longitudinal/data/plain_texts+meta/plain_corrected/'
    # meta_file = '/Users/zweiss/Documents/0_corpora/Karlsruhe_Childrens_Text/longitudinal/docs/MetaData_H1.csv'

    rewrite_all_files(input_dir, output_src, output_trgt, meta_file)