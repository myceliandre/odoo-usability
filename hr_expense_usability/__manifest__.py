# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Hr Expense Usability',
    'version': '12.0.1.0.0',
    'category': '',
    'license': 'AGPL-3',
    'summary': 'Usability improvements on hr expense module',
    'description': """
Hr expense Usability
==============

This module provides several small usability improvements on the official *hr_expense* module:

* Does not replace unit amount when changing product if already exist (import from mail or other automated import)
* TODO: update this list

This module has been written by Nicolas JEUDY from Mycéliandre <https://github.com/njeudy>.
    """,
    'author': 'Mycéliandre',
    'website': 'http://myceliandre.fr',
    'depends': [
        'hr_expense',
        ],
    'data': [
        ],
    'installable': True,
}
