def get_table_html(top_margin: int, table_name: str, col1_title: str, col2_title: str, **rows) -> str:
    rows = list(rows.items())
    table_html = f"""
    <div style="position: fixed; top: {top_margin}px; left: 20px; z-index: 1000; background-color: white; padding: 10px; border: 1px solid #ccc;">
        <style>
            table {{
                border-collapse: collapse;
                width: 100%;
            }}

            th, td {{
                border: 1px solid black;
                padding: 8px;
                text-align: center;
            }}

            th {{
                background-color: #f2f2f2;
            }}
        </style>
        <table>
            <tr>
                <th colspan="2">{table_name}</th>
            </tr>
            <tr>
                <th>{col1_title}</th>
                <th>{col2_title}</th>
            </tr>
            <tr>
                <td>{rows[0][0]}</td>
                <td>{rows[0][1]:.2f}</td>
            </tr>
            <tr>
                <td>{rows[1][0]}</td>
                <td>{rows[1][1]:.2f}</td>
            </tr>
            <tr>
                <td>{rows[2][0]}</td>
                <td>{rows[2][1]:.2f}</td>
            </tr>
        </table>
    </div>
    """
    return table_html


def get_legend_html(element_name: str) -> str:
    bus_legend_html = """
        <div style="position: fixed; 
        bottom: 200px; right: 50px; width: 150px; height: 180px; 
        border:0px solid grey; z-index:9999; font-size:14px;
        background-color: white;
        ">&nbsp; <span style="font-weight: bold; font-size: 20px">Bus Legends </span></b><br>
        &nbsp; <font color="red" style="font-size: 30px;">●</font><span style="font-weight:bold;"> |V| < 0.95</span>   <br>
        &nbsp; <font color="green" style="font-size: 30px;">●</font><span style="font-weight:bold;"> 0.95 ≤ |V| ≤ 1.05</span><br>
        &nbsp; <font color="yellow" style="font-size: 30px;">●</font><span style="font-weight:bold;"> 1.05 < |V|</span><br>
        </div>
        """
    line_legend_html = """
        <div style="position: fixed; 
        bottom: 20px; right: 20px; width: 200px; height: 180px; 
        border:0px solid grey; z-index:9999; font-size:14px;
        background-color: white;
        ">&nbsp; <span style="font-weight: bold; font-size: 20px">Line Legends </span></b><br>
        &nbsp; <font color="green" style="font-size: 30px;">—</font><span style="font-weight:bold;"> Loading ≤ 50%</span><br>
        &nbsp; <font color="orange" style="font-size: 30px;">—</font><span style="font-weight:bold;"> 50% ≤ Loading < 100%</span><br>
        &nbsp; <font color="red" style="font-size: 30px;">—</font><span style="font-weight:bold;"> Loading > 100%</span><br>
        </div>
        """
    if element_name == "bus":
        return bus_legend_html
    elif element_name == "line":
        return line_legend_html