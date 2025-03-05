def write_csv_file_headers(output_file, width, height, padding, nodespacing, levelspacing, edgespacing, refs_color, includes_color, extends_color,
                           refs_style, includes_style, extends_style):
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write("## Habit Tracker UML use case diagram\n")
        file.write("# label: %action%\n")
        file.write("# style: shape=%shape%;rounded=1;fillColor=%fill%;strokeColor=%stroke%;hyperlink=%action%;\n")
        file.write(f'# connect: {{"from":"refs", "to":"id", "style":"curved=0;endArrow=blockThin;endFill=1;dashed={refs_style};strokeColor={refs_color};"}}\n')
        file.write(f'# connect: {{"from":"includes", "to":"id", "style":"curved=0;endArrow=blockThin;endFill=1;dashed={includes_style};strokeColor={includes_color};"}}\n')
        file.write(f'# connect: {{"from":"extends", "to":"id", "style":"curved=0;endArrow=blockThin;endFill=1;dashed={extends_style};strokeColor={extends_color};"}}\n')
        file.write(f"# width: {width}\n")
        file.write(f"# height: {height}\n")
        file.write(f"# padding: {padding}\n")
        file.write(f"# nodespacing: {nodespacing}\n")
        file.write(f"# levelspacing: {levelspacing}\n")
        file.write(f"# edgespacing: {edgespacing}\n")
        file.write(f"# link: url\n")
        file.write("# layout: horizontalflow\n")
        file.write("## CSV data starts below this line\n")
        file.write("id,action,fill,stroke,shape,includes,extends,refs,url\n")

'''
id: уникальный идентификатор узла.
action: название действия или текст на узле.
fill: цвет заливки узла.
stroke: цвет обводки узла.
shape: форма узла (например, rectangle, ellipse).
includes: список ID узлов, которые включаются этим узлом.
extends: список ID узлов, которые расширяются этим узлом.
refs: список ссылок на другие узлы.
'''