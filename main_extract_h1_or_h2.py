
import sys
from annotated_document import *

if __name__ == '__main__':

    if len(sys.argv) < 5:
        print("Call:\n> python3 main_extract_h1_or_h2.py IN_DIR OUT_DIR_ORIGINAL OUT_DIR_CORRECTED OUT_FILE_META")
        exit(0)

    #example call:
    # python3 main_extract_h1_or_h2.py /Users/zweiss/Documents/LiteratureARessources/corpora/german-fla/Berkling_Corpora/H2/data/original/ /Users/zweiss/Documents/LiteratureARessources/corpora/german-fla/Berkling_Corpora/H2/data/plain_texts+meta/orig/ /Users/zweiss/Documents/LiteratureARessources/corpora/german-fla/Berkling_Corpora/H2/data/plain_texts+meta/corr/ /Users/zweiss/Documents/LiteratureARessources/corpora/german-fla/Berkling_Corpora/H2/data/plain_texts+meta/meta.csv
    # python3 main_extract_h1_or_h2.py /Users/zweiss/Documents/LiteratureARessources/corpora/german-fla/Berkling_Corpora/H1/data/original/Transcriptions/ /Users/zweiss/Documents/LiteratureARessources/corpora/german-fla/Berkling_Corpora/H1/data/plain_texts+meta/orig/ /Users/zweiss/Documents/LiteratureARessources/corpora/german-fla/Berkling_Corpora/H1/data/plain_texts+meta/corr/ /Users/zweiss/Documents/LiteratureARessources/corpora/german-fla/Berkling_Corpora/H1/data/plain_texts+meta/meta.csv

    in_dir = sys.argv[1]
    orig_out = sys.argv[2]
    corr_out = sys.argv[3]
    meta_file = sys.argv[4]

    os.makedirs(orig_out, exist_ok=True)
    os.makedirs(corr_out, exist_ok=True)

    be_verbose = False
    debug = False

    # get all files
    in_files = AnnotatedStudentWriting.rec_load_files(input_dir=in_dir, skip_a_files=True, file_ending=".csv")

    for i, cfile in enumerate(in_files):
        # load results
        tmp_doc = AnnotatedStudentWriting()
        if debug:
            tmp_doc.start_debug_mode()
        tmp_doc.load_h1_or_h2_file(in_file=cfile, be_verbose=be_verbose)
        # save results
        tmp_doc.save_original(out_file=os.path.join(orig_out, tmp_doc.file_name[:-4]+".txt"), without_annotaions=True)
        tmp_doc.save_corrected(out_file=os.path.join(corr_out, tmp_doc.file_name[:-4]+".txt"), without_annotaions=True)
        tmp_doc.save_meta_information(out_file=meta_file, delim=";", is_new_file=i==0)

    if be_verbose:
        print("Done.")

    # TODO Check issue files in H1:
    # Issue with file: t_H1.KC.G3.6.longterm.csv
    # Issue with file: t_H1.KB.G3.19.week4.csv
    # Issue with file: t_H1.KC.G2.12.week3.csv
    # Issue with file: t_H1.KC.G3.5.week3.csv
    # Issue with file: t_H1.KC.G3.11.week11.csv

    # TODO Check issue with files in H2:
    # Issue with file: t_H1.G4.KA.7.week7.csv
    # Issue with file: t_H1.G4.KB.21.week5.csv
    # Issue with file: t_H2.G2.KB.2.pretest.D.csv
    # Issue with file: t_H2.G2.KA.20.week4.csv
    # Issue with file: t_H2.G2.KA.22.week3.csv
    # Issue with file: t_H2.G4.KA.7.week7.csv
    # Issue with file: t_H2.G4.KA.5.week10.csv
    # Issue with file: t_H2.G3.KB.17.week8.csv
    # Issue with file: t_E2.G3.KA.1.week8.csv
    # Issue with file: t_ERK1.G3.KB.6.week8.csv
