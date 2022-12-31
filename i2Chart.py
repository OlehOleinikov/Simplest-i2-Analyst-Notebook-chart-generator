import random
from typing import List, Union
from pathlib import Path

from xml.etree.ElementTree import Element, SubElement, Comment
import xml.etree.ElementTree as ET
from xml.dom import minidom


def _hex_color_to_ibm_integer(hex_color):
    """Need to change RGB to BGR color scheme, then convert HEX to integer"""
    value = hex_color.lstrip('#')
    lv = len(value)
    rgb = tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
    rbg = (rgb[2], rgb[1], rgb[0])
    new_hex = '%02x%02x%02x' % rbg
    return str(int(new_hex, 16))


class IBMi2Graph:
    black = _hex_color_to_ibm_integer("000000")  # (0,0,0)
    white = _hex_color_to_ibm_integer("FFFFFF")  # (255,255,255)
    red = _hex_color_to_ibm_integer("FF0000")  # (255,0,0)
    lime = _hex_color_to_ibm_integer("00FF00")  # (0,255,0)
    blue = _hex_color_to_ibm_integer("0000FF")  # (0,0,255)
    yellow = _hex_color_to_ibm_integer("FFFF00")  # (255,255,0)
    cyan = _hex_color_to_ibm_integer("00FFFF")  # (0,255,255)
    magenta = _hex_color_to_ibm_integer("FF00FF")  # (255,0,255)
    silver = _hex_color_to_ibm_integer("C0C0C0")  # (192,192,192)
    gray = _hex_color_to_ibm_integer("808080")  # (128,128,128)
    maroon = _hex_color_to_ibm_integer("800000")  # (128,0,0)
    olive = _hex_color_to_ibm_integer("808000")  # (128,128,0)
    green = _hex_color_to_ibm_integer("008000")  # (0,128,0)
    purple = _hex_color_to_ibm_integer("800080")  # (128,0,128)
    teal = _hex_color_to_ibm_integer("008080")  # (0,128,128)
    navy = _hex_color_to_ibm_integer("000080")  # (0,0,128)

    chart_attrs = {'BackColour': white,
                   'BlankLinkLabels': 'true',
                   'DefaultDate': '2022-01-01T00:00:00.000',
                   'DefaultTickRate': '1',
                   'GridHeightSize': '0.295275590551181',
                   'GridVisibleOnAllViews': 'true',
                   'GridWidthSize': '0.295275590551181',
                   'HideMatchingTimeZoneFormat': 'false',
                   'ShowAllFlag': 'false',
                   'ShowPages': 'false',
                   'SnapToGrid': 'false',
                   'Rigorous': 'true',
                   'IdReferenceLinking': 'false',
                   'LabelRule': 'LabelRuleMerge',
                   'LabelSumNumericLinks': 'false',
                   'UseLocalTimeZone': 'true',
                   'UseWiringHeightForThemeIcon': 'true',
                   'WiringDistanceFar': '0.393700787401575',
                   'WiringDistanceNear': '0.078740157480315',
                   'WiringHeight': '0.196850393700787',
                   'WiringSpacing': '0.196850393700787',
                   'TimeBarVisible': 'false'}

    StrengthCollection = [{'DotStyle': 'DotStyleDashed', 'Id': 'Dashed', 'Name': 'Unconfirmed'},
                          {'DotStyle': 'DotStyleSolid', 'Id': 'Solid', 'Name': 'Confirmed'},
                          {'DotStyle': 'DotStyleDotted', 'Id': 'Tentative', 'Name': 'Tentative'}]

    EntityTypeCollection = [{'Name': 'PersonFirst', 'Colour': '0', 'IconFile': 'Prisoff',
                             'PreferredRepresentation': 'RepresentAsIcon'},
                            {'Name': 'PersonSecond', 'Colour': '0', 'IconFile': 'Prisoff US',
                             'PreferredRepresentation': 'RepresentAsIcon'},
                            {'Name': 'PersonOther', 'Colour': '0', 'IconFile': 'Person (Faceless)',
                             'PreferredRepresentation': 'RepresentAsIcon'},
                            {'Name': 'Car', 'Colour': '0', 'IconFile': 'Car',
                             'PreferredRepresentation': 'RepresentAsIcon'},
                            {'Name': 'Plate', 'Colour': '0', 'IconFile': 'Motor vehicle',
                             'PreferredRepresentation': 'RepresentAsIcon'},
                            {'Name': 'Van', 'Colour': '0', 'IconFile': 'Van',
                             'PreferredRepresentation': 'RepresentAsIcon'},
                            {'Name': 'Bus', 'Colour': '0', 'IconFile': 'Minibus',
                             'PreferredRepresentation': 'RepresentAsIcon'},
                            {'Name': 'Train', 'Colour': '0', 'IconFile': 'Train',
                             'PreferredRepresentation': 'RepresentAsIcon'},
                            {'Name': 'Plane', 'Colour': '0', 'IconFile': 'Terminal',
                             'PreferredRepresentation': 'RepresentAsIcon'},
                            {'Name': 'CheckPoint', 'Colour': '0', 'IconFile': 'Place',
                             'PreferredRepresentation': 'RepresentAsIcon'},
                            {'Name': 'Person', 'Colour': '0', 'IconFile': 'Person',
                             'PreferredRepresentation': 'RepresentAsIcon'}]

    LinkTypeCollection = [{'Name': 'Link', 'Colour': black},
                          {'Name': 'Fly', 'Colour': red},
                          {'Name': 'Car', 'Colour': blue},
                          {'Name': 'Walk', 'Colour': green},
                          {'Name': 'Use', 'Colour': purple}]

    SupportedEnlarge = ['ICEnlargeDouble', 'ICEnlargeHalf', 'ICEnlargeQuadruple',
                        'ICEnlargeSingle', 'ICEnlargeTriple']

    ArrowStyle = ['ArrowNone', 'ArrowOnBoth', 'ArrowOnHead', 'ArrowOnTail']

    def __init__(self):

        self.chart = Element('Chart')  # root
        intro_comment = Comment('Simple Python to IBM i2 ANB converter (by @matematik_777)')
        self.chart.append(intro_comment)
        for attr, value in self.chart_attrs.items():
            self.chart.set(attr, value)

        self.chart.append(self._get_collection(self.StrengthCollection, 'StrengthCollection', 'Strength'))
        self.chart.append(self._get_collection(self.EntityTypeCollection, 'EntityTypeCollection', 'EntityType'))
        self.chart.append(self._get_collection(self.LinkTypeCollection, 'LinkTypeCollection', 'LinkType'))

        self.items = SubElement(self.chart, 'ChartItemCollection')
        self.available_id = set()

    @staticmethod
    def _get_collection(settings: List[dict], collection: str, element_tag: str) -> Element:
        """Fill element attributes from dict"""
        local_root = Element(collection)
        for line in settings:
            new_elem = Element(element_tag)
            for attr, val in line.items():
                new_elem.set(attr, val)
            local_root.append(new_elem)
        return local_root

    def add_entity(self,
                   anb_type: str,
                   entity_id: int,
                   entity_identity: str,
                   entity_label: str = '',
                   entity_desc: str = '',
                   icon_size: str = 'ICEnlargeSingle',
                   show_label: bool = False,
                   show_description: bool = True,
                   wrap_subitem: bool = True,
                   wrap_width: float = 1.9685039370078741,
                   font_bold: bool = False,
                   font_size: int = 11):

        supported = [x.get('Name') for x in self.EntityTypeCollection]
        assert anb_type in supported, f'Type "{anb_type}"  is not defined (defined list: {str(supported)})'
        assert icon_size in self.SupportedEnlarge, f'Size "{icon_size}"  not supported ({str(self.SupportedEnlarge)})'
        self.available_id.add(entity_id)

        new_item = Element('ChartItem')
        position_x = random.randint(0, 1000)
        position_y = random.randint(0, 1000)
        item_settings = {'DateSet': 'false',
                         'GradeOneIndex': '0',
                         'Description': entity_desc,
                         'GradeTwoIndex': '0',
                         'Selected': 'false',
                         'GradeThreeIndex': '0',
                         'TimeSet': 'false',
                         'Ordered': 'false',
                         'Label': entity_label,
                         'Shown': str(True).lower(),
                         'XPosition': str(position_x)}
        for attr, val in item_settings.items():
            new_item.set(attr, val)

        end = SubElement(new_item, 'End')
        end.set('Y', str(position_y))
        end.set('X', str(position_x))
        end.set('Z', '0')

        entity = SubElement(end, 'Entity')
        entity.set('EntityId', str(entity_id))
        entity.set('Identity', entity_identity)
        entity.set('LabelIsIdentity', 'true')

        icon = SubElement(entity, 'Icon')
        icon.set('TextX', '0')
        icon.set('TextY', '20')

        style = SubElement(icon, 'IconStyle')
        style.set('Enlargement', icon_size)
        style.set('Type', anb_type)

        CIStyle = SubElement(new_item, 'CIStyle')
        CIStyle.set('Background', 'false')
        CIStyle.set('DateTimeFormat', 'Default')
        CIStyle.set('ShowDateTimeDescription', 'false')
        CIStyle.set('UseSubTextWidth', str(wrap_subitem).lower())
        CIStyle.set('SubTextWidth', str(wrap_width))

        font = SubElement(CIStyle, 'Font')
        font.set('BackColour', self.white)
        font.set('FontColour', self.black)
        font.set('CharSet', 'CharSetANSI')
        font.set('FaceName', 'Tahoma')
        font.set('PointSize', str(font_size))
        font.set('Bold', str(font_bold).lower())
        font.set('Italic', 'false')
        font.set('Underline', 'false')
        font.set('Strikeout', 'false')

        subitem = SubElement(CIStyle, 'SubItemCollection')
        subitem_settings = {'SubItemDescription': show_description,
                            'SubItemGrades': False,
                            'SubItemLabel': show_label,
                            'SubItemPin': False,
                            'SubItemSourceReference': False,
                            'SubItemSourceType': False,
                            'SubItemDateTime': False}
        for si_type, val in subitem_settings.items():
            cur_si_type = SubElement(subitem, 'SubItem')
            cur_si_type.set('Type', si_type)
            cur_si_type.set('Visible', str(val).lower())
        self.items.append(new_item)

    def add_link(self,
                 id1: int,
                 id2: int,
                 entity_label: str = '',
                 show_label=True,
                 entity_desc: str = '',
                 show_description=False,
                 wrap_subitem=True,
                 wrap_width=1.9685039370078741,
                 width=1,
                 strength='Confirmed',
                 link_type='Link',
                 arrow='ArrowNone'):
        links_t = [x.get('Name') for x in self.LinkTypeCollection]
        stren_t = [x.get('Name') for x in self.StrengthCollection]
        assert strength in stren_t, f'Strength "{strength}" is not set, use known types ({str(stren_t)})"'
        assert link_type in links_t, f'Link type {link_type} is not set, use known types ({str(links_t)})'
        assert id1 in self.available_id, f'ID{id1} is absent.'
        assert id2 in self.available_id, f'ID{id2} is absent.'
        assert arrow in self.ArrowStyle, f'Arrow "{str(arrow)}" style not allow. Use instead: {str(self.ArrowStyle)}'
        assert 0 <= width <= 32, f'Width line should be in range 0....32 (current value = {width})'
        assert id1 != id2

        new_item = Element('ChartItem')
        item_settings = {'DateSet': 'false',
                         'GradeOneIndex': '0',
                         'Description': entity_desc,
                         'GradeTwoIndex': '0',
                         'Selected': 'false',
                         'GradeThreeIndex': '0',
                         'TimeSet': 'false',
                         'Ordered': 'false',
                         'Label': entity_label,
                         'Shown': str(True).lower(),
                         'XPosition': str(0)}
        for attr, val in item_settings.items():
            new_item.set(attr, val)

        link = SubElement(new_item, 'Link')
        link.set('End1Id', str(id1))
        link.set('End2Id', str(id2))
        link.set('LabelPos', '50')
        link.set('LabelSegment', '0')
        link.set('Offset', '0')

        style = SubElement(link, 'LinkStyle')
        style.set('ArrowStyle', arrow)
        style.set('LineWidth', str(width))
        style.set('Strength', strength)
        style.set('Type', link_type)

        CIStyle = SubElement(new_item, 'CIStyle')
        CIStyle.set('Background', 'false')
        CIStyle.set('DateTimeFormat', 'Default')
        CIStyle.set('ShowDateTimeDescription', 'false')
        CIStyle.set('UseSubTextWidth', str(wrap_subitem).lower())
        CIStyle.set('SubTextWidth', str(wrap_width))

        font = SubElement(CIStyle, 'Font')
        font.set('BackColour', self.white)
        font.set('FontColour', self.black)
        font.set('CharSet', 'CharSetANSI')
        font.set('FaceName', 'Tahoma')
        font.set('PointSize', '11')
        font.set('Bold', 'false')
        font.set('Italic', 'false')
        font.set('Underline', 'false')
        font.set('Strikeout', 'false')

        subitem = SubElement(CIStyle, 'SubItemCollection')
        subitem_settings = {'SubItemDescription': show_description,
                            'SubItemGrades': False,
                            'SubItemLabel': show_label,
                            'SubItemPin': False,
                            'SubItemSourceReference': False,
                            'SubItemSourceType': False,
                            'SubItemDateTime': False}
        for si_type, val in subitem_settings.items():
            cur_si_type = SubElement(subitem, 'SubItem')
            cur_si_type.set('Type', si_type)
            cur_si_type.set('Visible', str(val).lower())
        self.items.append(new_item)

    def chart_to_string(self) -> str:
        return minidom.parseString(ET.tostring(self.chart)).toprettyxml(indent="   ")

    def save_file(self, file: Union[str, Path]):
        """Generate *.anx file"""
        if type(file) is not Path:
            file = Path(file)
        file = file.with_suffix('.anx')
        content = self.chart_to_string()
        with open(file.absolute(), 'w', encoding='UTF-8') as f:
            f.write(content)
