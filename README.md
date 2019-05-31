# KCTErrorExtractor
Extracts error types from the Karslruhe Childrens' Texts corpus. This code was used for the extraction of errors in the article Weiss & Meurers (2019).

**annotated_document.py** reads documents in the format of the KCT corpus (Lavalley et al. 2015) or the H1/H2 corpus (Berkling 2016, 2018) and retrieves information on different error types from it. You may output the target hypothesis and the original writing as two sperate plain text files and additionally extract statistics on different error types saved in a separate csv.

See **main_extract_h1_or_h2.py** and **main_extract_kct.py** for use examples.

## References

* Berkling, K. (2018). A 2nd Longitudinal Corpus for Children's Writing with Enhanced Output for Specific Spelling Patterns. In Proceedings of the Eleventh International Conference on Language Resources and Evaluation (LREC-2018).
* Berkling, K. (2016). Corpus for Children's Writing with Enhanced Output for Specific Spelling Patterns (2nd and 3rd Grade). In LREC.
* Lavalley, R., Berkling, K., & Stüker, S. (2015). Preparing children's writing database for automated processing. In LTLT@ SLaTE (pp. 9-15).
* Weiss, Z., Meurers, D. (2019). Analyzing Linguistic Complexity and Accuracy in Academic Language
Development of German across Elementary and Secondary School. In Proceedings of the 14th Workshop on Innovative Use of NLP for Building Educational Applications.
