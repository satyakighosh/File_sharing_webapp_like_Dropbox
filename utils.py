import random
import string
 
def get_random_string(str_size = 10):
    allowed_chars = string.ascii_letters + string.punctuation
    return ''.join(random.choice(allowed_chars) for x in range(str_size))

def allowed_file(filename):
    #JPG, GIF, PNG, DOC, DOCX, XLS, XLSX, PPT, PPTX, PDF, CSV 
    ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'gif', 'png', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'pdf', 'csv']
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

 
