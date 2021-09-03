import secrets

def generate_filename(extension: str) -> str:
    return '{}.{}'.format(secrets.token_hex(nbytes=16), extension)

def get_extenstion(filename: str) -> str:
    filename_parts = filename.split('.')
    if len(filename_parts) > 1:
        return filename_parts[-1]
    return ''

def save_file(folder, uploaded_file) -> str:
    if uploaded_file:
        extension = get_extenstion(uploaded_file.filename)
        filename = generate_filename(extension)
        
        file_location = 'files/{}/{}'.format(folder, filename)
        
        with open(file_location, 'wb+') as file_object:
            file_object.write(uploaded_file.file.read())

        return filename