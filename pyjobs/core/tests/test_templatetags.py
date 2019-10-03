from django.test import SimpleTestCase, RequestFactory
from django.template import Context, Template


class TestMergeQueryParamsTag(SimpleTestCase):
    def setUp(self):
        self.rf = RequestFactory()

    def test_add_param(self):
        request = self.rf.get("/", {"description": "descricao", "salary_range": 1})
        context = Context({"request": request})
        template = Template(
            "{% load core_tags %}"
            '<a class="page-link" href="/?{% merge_query_params page=1 %}">1</a>'
        )
        rendered_template = template.render(context)

        self.assertInHTML(
            '<a class="page-link" href="/?description=descricao&salary_range=1&page=1">1</a>',
            rendered_template,
        )

    def test_replace_param(self):
        request = self.rf.get(
            "/", {"description": "descricao", "salary_range": 1, "page": 2}
        )
        context = Context({"request": request})
        template = Template(
            "{% load core_tags %}"
            '<a class="page-link" href="/?{% merge_query_params page=10 %}">1</a>'
        )
        rendered_template = template.render(context)

        self.assertInHTML(
            '<a class="page-link" href="/?description=descricao&salary_range=1&page=10">1</a>',
            rendered_template,
        )
