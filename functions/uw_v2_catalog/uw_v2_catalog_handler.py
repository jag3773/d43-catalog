# -*- coding: utf-8 -*-

#
# Class for converting the catalog into a format compatible with the v2 api.
#

import time
from datetime import datetime

def datestring_to_timestamp(datestring):
    return str(int(time.mktime(datetime.strptime(datestring[:10], "%Y-%m-%d").timetuple())))

class UwV2CatalogHandler:

    def __init__(self, catalog):
        """
        Initializes the converter with the catalog from which to generate the v2 catalog
        :param catalog: the latest catalog
        """
        self.latest_catalog = catalog

    def convert_catalog(self):
        """
        Generates the v2 catalog
        :return: the v2 form of the catalog
        """
        v2_catalog = {
            'obs': {},
            'bible': {}
        }

        res_map = {
            'ulb': 'bible',
            'udb': 'bible',
            'obs': 'obs'
        }

        title_map = {
            'bible': 'Bible',
            'obs': 'Open Bible Stories'
        }

        last_modified = 0

        for lang in self.latest_catalog['languages']:
            lang_slug = lang['identifier']
            for res in lang['resources']:
                res_type = res['identifier']
                print(res_type)
                key = res_map[res_type] if res_type in res_map else None

                if not key:
                    continue

                mod = datestring_to_timestamp(res['modified'])

                if int(mod) > last_modified:
                    last_modified = int(mod)

                # TODO: figure out how to handle "formats" and the chunks

                toc = []
                for proj in res['projects']:
                    toc.append({
                        'desc': '',
                        'media': {},
                        'mod': mod,
                        'slug': proj['identifier'],
                        'src': '',
                        'src_sig': '',
                        'title': proj['title'],
                    })

                source = res['source'][0]
                comment = ''
                if 'comment' in res:
                    comment = res['comment']
                res_v2 = {
                    'slug': res_type, # TODO: check if should have lang_slug
                    'name': res['title'],
                    'mod': mod,
                    'status': {
                        'checking_entity': '; '.join(res['checking']['checking_entity']),
                        'checking_level': res['checking']['checking_level'],
                        'comments': comment,
                        'contributors': '; '.join(res['contributor']),
                        'publish_date': res['issued'],
                        'source_text': source['identifier'] + '-' + source['language'],
                        'source_text_version': source['version'],
                        'version': res['version']
                    },
                    'toc': toc
                }

                if not lang_slug in v2_catalog[key]:
                    v2_catalog[key][lang_slug] = {
                        'lc': lang_slug,
                        'mod': mod,
                        'vers': []
                    }
                v2_catalog[key][lang_slug]['vers'].append(res_v2)

        # condense catalog
        catalog = {
            'cat': [],
            'mod': last_modified
        }
        for cat_slug in v2_catalog:
            langs = []
            for lang_slug in v2_catalog[cat_slug]:
                langs.append(v2_catalog[cat_slug][lang_slug])

            catalog['cat'].append({
                'slug': cat_slug,
                'title': title_map[cat_slug],
                'langs': langs
            })

        return catalog