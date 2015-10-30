__author__ = 'ryoungblood'
'''
with TopikProject("filename", parameters_for_backend) as project:
    raw_input = read_input(file_to_load, project, )
    # apply filters
    filtered_data = raw_input.filter()
    result = project.tokenize(filtered_data, method=, data_filters)
    vectorize(project, method=, OR specify tokenization method) # if


class TopikProject(object):
    def tokenize(self):
        return functools.partial(tokenize, project=self)
'''