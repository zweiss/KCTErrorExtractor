
import sys
from annotated_document import *

if __name__ == '__main__':

    if len(sys.argv) < 5:
        print("Call:\n> python3 main_extract_kct.py IN_DIR OUT_DIR_ORIGINAL OUT_DIR_CORRECTED OUT_FILE_META")
        exit(0)
    # python3 main_extract_kct.py /Users/zweiss/Documents/LiteratureARessources/corpora/german-fla/Berkling_Corpora/Karlsruhe_Childrens_Texts/data/original/  /Users/zweiss/Documents/LiteratureARessources/corpora/german-fla/Berkling_Corpora/Karlsruhe_Childrens_Texts/data/plain_texts+meta/orig/  /Users/zweiss/Documents/LiteratureARessources/corpora/german-fla/Berkling_Corpora/Karlsruhe_Childrens_Texts/data/plain_texts+meta/corr/  /Users/zweiss/Documents/LiteratureARessources/corpora/german-fla/Berkling_Corpora/Karlsruhe_Childrens_Texts/data/plain_texts+meta/meta.csv

    in_dir = sys.argv[1]
    orig_out = sys.argv[2]
    corr_out = sys.argv[3]
    meta_file = sys.argv[4]

    os.makedirs(orig_out, exist_ok=True)
    os.makedirs(corr_out, exist_ok=True)

    be_verbose = False
    debug = False

    # get all files
    in_files = AnnotatedStudentWriting.rec_load_files(input_dir=in_dir, skip_a_files=False, file_ending=".txt")

    for i, cfile in enumerate(in_files):
        # load results
        tmp_doc = AnnotatedStudentWriting()
        if debug:
            tmp_doc.start_debug_mode()
        tmp_doc.load_kct_file(in_file=cfile, be_verbose=be_verbose)
        # save results
        tmp_doc.save_original(out_file=os.path.join(orig_out, tmp_doc.file_name), without_annotaions=True)
        tmp_doc.save_corrected(out_file=os.path.join(corr_out, tmp_doc.file_name), without_annotaions=True)
        tmp_doc.save_meta_information(out_file=meta_file, delim=";", is_new_file=i==0)

    if be_verbose:
        print("Done.")




    # TODO fix issue with these files
    #Issue with file: 5_0320.txt
    #Issue with file: 2_0107.txt
    #Issue with file: 2_0303.txt
    #Issue with file: 5_0177.txt
    #Issue with file: 2_0130.txt
    #Issue with file: 2_0139.txt
    #Issue with file: 3_0020.txt
    #Issue with file: 5_0176.txt
    #Issue with file: 2_0248.txt
    #Issue with file: 2_0222.txt
    #Issue with file: 1_0000.txt
    #Issue with file: 2_0249.txt
    #Issue with file: 2_0433.txt
    #Issue with file: 5_0283.txt
    #Issue with file: 5_0278.txt
    #Issue with file: 2_0466.txt
    #Issue with file: 2_0208.txt
    #Issue with file: 2_0239.txt
    #Issue with file: 5_0213.txt
    #Issue with file: 2_0522.txt
    #Issue with file: 1_0160.txt
    #Issue with file: 5_0368.txt
    #Issue with file: 4_0011.txt
    #Issue with file: 2_0125.txt
    #Issue with file: 2_0159.txt
    #Issue with file: 2_0331.txt
    #Issue with file: 5_0129.txt
    #Issue with file: 2_0300.txt
    #Issue with file: 3_0078.txt
    #Issue with file: 4_0054.txt
    #Issue with file: 2_0301.txt
    #Issue with file: 5_0054.txt
    #Issue with file: 5_0409.txt
    #Issue with file: 5_0052.txt
    #Issue with file: 2_0040.txt
    #Issue with file: 5_0267.txt
    #Issue with file: 2_0244.txt
    #Issue with file: 2_0071.txt
    #Issue with file: 2_0219.txt
    #Issue with file: 1_0026.txt
    #Issue with file: 2_0261.txt
    #Issue with file: 1_0020.txt
    #Issue with file: 2_0256.txt
    #Issue with file: 3_0116.txt
    #Issue with file: 5_0243.txt
    #Issue with file: 5_0049.txt
    #Issue with file: 2_0260.txt
    #Issue with file: 3_0120.txt
    #Issue with file: 1_0106.txt
    #Issue with file: 2_0116.txt
    #Issue with file: 5_0168.txt
    #Issue with file: 5_0194.txt
    #Issue with file: 5_0503.txt
