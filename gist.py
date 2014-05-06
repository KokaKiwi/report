import requests
import json

class File(object):
    def __init__(self, name, content, **kwargs):
        self.name = name
        self.content = content

        self.language = None

        for (name, value) in kwargs.items():
            setattr(self, name, value)

    @property
    def data(self):
        data = {}

        data['content'] = self.content

        if self.language is not None:
            data['language'] = self.language

        return data

BASE_URL = 'https://api.github.com'

class Gist(object):
    public = True

    def __init__(self, **kwargs):
        self.description = None

        self.username = None
        self.api_key = None

        self.files = []

        for (name, value) in kwargs.items():
            setattr(self, name, value)

    def add_file(self, *args, **kwargs):
        file = File(*args, **kwargs)
        self.files.append(file)

    @property
    def data(self):
        data = {}

        data['files'] = {}
        for file in self.files:
            data['files'][file.name] = file.data

        if self.description is not None:
            data['description'] = self.description

        data['public'] = self.public

        return data

    @property
    def json(self):
        return json.dumps(self.data)

    @property
    def headers(self):
        headers = {}

        headers['Content-Type'] = 'application/json'

        if self.username is not None:
            headers['X-Github-Username'] = self.username

        if self.api_key is not None:
            headers['Authorization'] = 'token {}'.format(self.api_key)

        return headers

    def create(self):
        url = '{base_url}/gists'.format(base_url = BASE_URL)

        r = requests.post(url, data = self.json, headers = self.headers)

        if r.status_code == 201:
            res = r.json()

            return {
                'id': res['id'],
                'created_at': res['created_at'],
                'url': res['html_url'],
                'git_clone_url': res['git_pull_url'],
                'git_push_url': res['git_push_url'],
            }

        raise Exception('Gist not created.')

if __name__ == '__main__':
    gist = Gist()
    gist.add_file('test.c', 'int main() {}')

    res = gist.create()
    print('Gist URL:', res['url'])
