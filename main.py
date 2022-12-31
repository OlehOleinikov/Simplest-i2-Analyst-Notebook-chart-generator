from i2Chart import IBMi2Graph


if __name__ == '__main__':
    i2 = IBMi2Graph()
    i2.add_entity(entity_id=1,
                  entity_label='Custom label...',
                  entity_identity='First entity identity',
                  anb_type='PersonFirst',
                  icon_size='ICEnlargeSingle',
                  entity_desc='It is description... It can be long string with wrapping. Label is hidden in this case.')
    i2.add_entity(entity_id=2,
                  entity_label='Custom label again',
                  entity_identity='Identity for second entity (without wrapping)',
                  anb_type='Train',
                  icon_size='ICEnlargeDouble',
                  entity_desc='my description',
                  show_description=False,
                  show_label=True)
    i2.add_entity(entity_id=3,
                  entity_identity='Some another ID',
                  anb_type='Person',
                  icon_size='ICEnlargeSingle',
                  entity_desc='Regular person')
    i2.add_entity(entity_id=4,
                  entity_identity='ID283',
                  entity_desc='Another long text subitem description... With font parameters',
                  font_size=18,
                  font_bold=True,
                  anb_type='Plane')

    i2.add_link(1, 2,
                show_label=True,
                entity_label='This is a link label',
                entity_desc='This is a description with wrapping ',
                width=1,
                link_type='Link',
                arrow='ArrowOnBoth',
                strength='Unconfirmed')
    i2.add_link(3, 2,
                show_label=True,
                show_description=True,
                entity_label='This is a link label',
                entity_desc='This is a description with wrapping ',
                width=3,
                link_type='Car',
                arrow='ArrowNone',
                strength='Tentative')
    i2.add_link(2, 4,
                show_label=True,
                entity_label='This is a link label',
                entity_desc='This is a description with wrapping ',
                width=5,
                link_type='Fly',
                arrow='ArrowOnHead',
                strength='Confirmed')
    i2.save_file('test_chart.anx')
