"""File with queries"""


GET_ARTICLE_TO_DO = 'SELECT header, habr_id, url ' \
                    'FROM db_manager_articles ' \
                    'WHERE parse_this = 1'
"""Query to get articles, that have 'parse_this' = 1"""

GET_HUB_TO_DO = 'SELECT name, url, last_parsed, parse_interval_minutes, id ' \
                'FROM db_manager_habrs ' \
                'WHERE is_active = true'
"""Query to get Habrs, that are activated by User"""

INSERT_TEMPLATE = "INSERT INTO {}({}) VALUES ({})"
"""Template to be used, to create an 'INSERT-query'"""

INSERT_OR_IGNORE_TEMPLATE = "INSERT OR IGNORE INTO {}({}) VALUES ({})"
"""Template to be used, to create an 'INSERT_OR_IGNORE-query'"""

UPDATE_TEMPLATE = "UPDATE {table} SET {updates} WHERE {conditions};"
"""Template to be used, to create an 'UPDATE-query'"""
