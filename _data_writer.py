import json
from datetime import datetime


class DataWriter(object):

    def __init__(self, root: str, archive_root: str = None):
        self._root = self._replace_delim(root, True)
        if archive_root:
            self._archive_root = self._replace_delim(archive_root, True)

    @staticmethod
    def _replace_delim(path: str, ensure_ends_with_slash: bool = False):
        new_path = path.replace('\\', '/')
        if ensure_ends_with_slash and new_path[-1] != '/':
            new_path = new_path + '/'
        return new_path

    def write_dictionary_as_json(self, filename: str, dictionary: dict, archive: bool = False):
        output_dictionary = {'data': dictionary}
        output_dictionary['timestamp'] = datetime.now().isoformat()
        with open(self._root + self._replace_delim(filename), 'w') as f:
            f.write(json.dumps(output_dictionary, indent=4))
        if archive and self._archive_root is not None:
            split_name = filename.split('.')
            if len(split_name) > 1:
                file_extension = split_name.pop()
            else:
                file_extension = ''
            filename = '.'.join(split_name)
            archive_filename = self._archive_root + filename + '/' + output_dictionary['timestamp'][0:19].replace(':',
                                                                                                                 '') + '_' + filename + '.' + file_extension
            with open(archive_filename, 'w') as fa:
                fa.write(json.dumps(output_dictionary, indent=4))
