#check file extensions
def allowed_file(filename):
    allowed_exts = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_exts
