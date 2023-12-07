from django.db import models


class Habrs(models.Model):
    """Represents Habrs - pages with articles on a specific topic

    Attributes:
        name: Habr's name, for convenience
        url: URL of a Habr
        last_parsed: DateTime, represents last DT when this Habr was parsed
        last_status: Represents last status of last parsing (success/failed)
        parse_interval_minutes: Interval of parsing in minutes
        is_active: True, if this Habr should be parsed, False to turn it off from parsing"""

    name = models.CharField(unique=True, max_length=100, verbose_name='Название Хабра')
    url = models.URLField()
    last_parsed = models.DateTimeField(null=True, blank=True, verbose_name='Последний парсинг')
    last_status = models.CharField(max_length=100, null=True, blank=True, verbose_name='Статус последнего парсинга')
    parse_interval_minutes = models.PositiveIntegerField(default=10, verbose_name='Интервал парсинга (минуты)')
    is_active = models.BooleanField(default=False, verbose_name='On/Off')

    def __str__(self):
        return self.name


class Articles(models.Model):
    """Represents articles, that need to be parsed

    Attributes:
        habr: Link to a Habr, where this article is related
        url: URL to this article
        date_collected: DT, when this article was initially collected from Habr's main page
        date_parsed: DT, when this article's data (text, author, etc.) was parsed
        last_status: Represents last status of last parsing (success/failed)
        parse_this: Set this to 1, and parser will parse this article (again or initially)
        header: Header for the article
        article_text: Main text for this article
        article_date: Date of the article
        author_name: Name of the author for this article
        author_url: URL to a page of the author of this article"""

    habr = models.ForeignKey(Habrs, on_delete=models.CASCADE)
    url = models.URLField()
    date_collected = models.DateTimeField(null=True, blank=True, verbose_name='Дата получения')
    date_parsed = models.DateTimeField(null=True, blank=True, verbose_name='Дата парсинга')
    last_status = models.CharField(max_length=100, null=True, blank=True, verbose_name='Статус последнего парсинга')
    parse_this = models.BooleanField(default=True, verbose_name='Спарсить')

    header = models.TextField(null=True, blank=True, unique=True, verbose_name='Заголовок')
    article_text = models.TextField(null=True, blank=True, verbose_name='Текст статьи')
    article_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата публикации')
    author_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='Автор')
    author_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"{self.header} - {self.habr}"


class ParserLogs(models.Model):
    """Logs for parsers

    Attributes:
        parser_name: Name of the parse, which made this log
        log_dt: DT, when this log was made
        log_text: Text of a log"""

    parser_name = models.CharField(max_length=100, verbose_name='Имя парсера')
    log_dt = models.DateTimeField(null=True, blank=True, verbose_name='Дата/Время сообщения')
    log_text = models.TextField(null=True, blank=True, verbose_name='Текст лога')
