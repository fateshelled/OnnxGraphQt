from NodeGraphQt import NodeGraph
from NodeGraphQt.base.menu import NodeGraphMenu

def set_context_menu_style(graph:NodeGraph, text_color, bg_color, selected_color, disabled_text_color=None):
    context_menu: NodeGraphMenu = graph.get_context_menu("graph").qmenu
    style = get_context_menu_stylesheet(text_color, bg_color, selected_color, disabled_text_color)
    context_menu.setStyleSheet(style)

def get_context_menu_stylesheet(text_color, bg_color, selected_color, disabled_text_color=None):
    if disabled_text_color is None:
        disabled_text_color =[int(0.5 * abs(text_color[i] + bg_color[i])) for i in range(3)]
    style_dict = {
        'QMenu': {
            'color': 'rgb({0},{1},{2})'.format(*text_color),
            'background-color': 'rgb({0},{1},{2})'.format(*bg_color),
            'border': '1px solid rgba({0},{1},{2},30)'.format(*text_color),
            'border-radius': '3px',
        },
        'QMenu::item': {
            'padding': '5px 18px 2px',
            'background-color': 'transparent',
        },
        'QMenu::item:selected': {
            'color': 'rgb({0},{1},{2})'.format(*text_color),
            'background-color': 'rgba({0},{1},{2},200)'
                                .format(*selected_color),
        },
        'QMenu::item:disabled': {
            'color': 'rgb({0},{1},{2})'.format(*disabled_text_color),
        },
        'QMenu::separator': {
            'height': '1px',
            'background': 'rgba({0},{1},{2}, 50)'.format(*text_color),
            'margin': '4px 8px',
        }
    }
    stylesheet = ''
    for css_class, css in style_dict.items():
        style = '{} {{\n'.format(css_class)
        for elm_name, elm_val in css.items():
            style += '  {}:{};\n'.format(elm_name, elm_val)
        style += '}\n'
        stylesheet += style
    return stylesheet