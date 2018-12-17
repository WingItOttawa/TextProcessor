import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
import git
from bs4 import BeautifulSoup
import json

class TextProcessor:
    def __init__(self):
        # Create database connection
        # TODO: Hide service-key code away from pipeline code, or at least put it in a function elsewhere
        dir_path = os.path.dirname(os.path.realpath(__file__))
        git_repo = git.Repo(dir_path, search_parent_directories=True)
        git_root_dir = git_repo.git.rev_parse("--show-toplevel")
        service_key_path = os.path.join(git_root_dir, 'wingit-service-key.json')
        cred = credentials.Certificate(service_key_path)
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    def main(self):
        docs = self.db.collection(u'filter').get()
        for doc in docs:
            id = doc.id
            doc_dict = doc.to_dict()
            content = doc_dict['content']
            soup = BeautifulSoup(content, 'html.parser')
            for s in soup(['script', 'style']):
                s.decompose()
        	body = soup.get_text(separator=' ').lower() # Replaces line breaks as seen on website through <br>, <div>, etc tags with space
        	body = ''.join([i if ord(i) > 96 and ord(i) < 123 else ' ' for i in body]) # Replaces anything non alphabetical to a space (except for ".")
        	body = body.replace('\n', ' ') # Replaces new lines with space
        	body = ' '.join(body.split()) # Takes one or more consecutive spaces and shrinks to a single space

            doc_dict['content'] = body

            doc_ref = self.db.collection(u'master').document(id)
            doc_ref.set(json.loads(json.dumps(doc_dict)))

            # TODO: Convert contractions to words (we're -> we are, shouldn't -> should not), or maybe remove them altogether.

if __name__ == "__main__":
    try:
        textprocessor = TextProcessor()
        textprocessor.main()
    except KeyboardInterrupt:
        pass
