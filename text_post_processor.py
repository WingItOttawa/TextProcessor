import os
import traceback
from difflib import SequenceMatcher

'''
TextPostProcessor applies additional processing on the crawled articles after crawling has been finished; this processing involves removing common substrings found in the articles.

To run this script, run:
python3 text_post_processor.py
---------------------------------------------
Logic:
Get array of longest common substring between f1 and f2 (>= 40 characters), then iterate through substring list and see how many in other crawled pages match.
If the occurence of a substring in other crawled pages is less than the threshold (0.5), remove substring from the substring list.
Add the remaining strings to the final list of substrings to remove.
Repeat process with f2 and f3, f3 and f4, f4 and f5, etc..

Definitely not the most efficient method right now as we have to go walk through all files and find longest common substrings which takes time.
Time is O(n) right now, but if a publication is fully crawled it would take way too long.

Another way we could potentially do it is randomize the article orders; right now the articles are listed alphabetically, and there could be some patterns
in the titles which could lead to undesired attention on the files that contain the same longest common substrings.

It would be better if all the longest common substrings in the publication were spread out evenly; that way we could only look for the long common substrings
in only some of the files, not all of them. After a certain point, we could then assume that those long common substrings are all that needed, and then remove
them in the rest of the files.
'''

class TextPostProcessor():

    min_match_length = 40
    substring_match_threshold = 0.05

    def __init__(self, publication_dir):
        self.publication_dir = publication_dir

    def process_articles(self):
        def get_as_single_line(dirpath, filename):
            with open(os.path.join(dirpath, filename), 'r') as file:
                return " ".join(file.readlines())

        strs_to_remove = []

        for (dirpath, dirnames, filenames) in os.walk(self.publication_dir):
            num_files = len(filenames)
            for i in range(num_files - 1):
                print ("% complete: ", float(i)/(num_files - 1) * 100)
                #Compares the nth file to the n + 1th file, then the n + 1th to the n + 2th, etc..
                comparator = get_as_single_line(dirpath, filenames[i])
                comparable = get_as_single_line(dirpath, filenames[i+1])
                match = SequenceMatcher(None, comparator, comparable, autojunk=False).find_longest_match(0, len(comparator), 0, len(comparable))
                temp_strs_to_remove = {}
                #If longest match is >= min_match_length, remove the longest match from the comparator string and find longest match again.
                #Exit once longest match is < min_match_length
                while self.min_match_length <= match.size:
                    match_str = comparator[match.a: match.a + match.size]
                    temp_strs_to_remove[match_str] = 0
                    comparator = comparator.replace(match_str, " ")
                    match = SequenceMatcher(None, comparator, comparable, autojunk=False).find_longest_match(0, len(comparator), 0, len(comparable))

                for x in range(num_files):
                    if x == i or x == i + 1:
                        continue
                    curr_text = get_as_single_line(dirpath, filenames[x])
                    for match_str in temp_strs_to_remove:
                        if match_str in curr_text:
                            temp_strs_to_remove[match_str] += 1

                file_threshold = self.substring_match_threshold * num_files
                final_strs_to_remove = []
                for match_str in temp_strs_to_remove:
                    if temp_strs_to_remove[match_str] >= file_threshold:
                        final_strs_to_remove.append(match_str)

                for filename in filenames:
                    curr_text = get_as_single_line(dirpath, filename)
                    curr_text_modified = False
                    for str in final_strs_to_remove:
                        if str in curr_text:
                            if not curr_text_modified:
                                curr_text_modified = True
                            curr_text = curr_text.replace(str, "")

                    if curr_text_modified:
                        with open(os.path.join(dirpath, filename), "w") as file:
                            file.write(curr_text)

if __name__ == '__main__':
    try:
        data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")
        text_post_processor = TextPostProcessor(publication_dir=data_dir)
        text_post_processor.process_articles()
    except KeyboardInterrupt:
        print("KeyboardInterrupt exception, exiting")
    except Exception as e:
        print("General exception in text_post_processor")
        print(traceback.format_exc())
