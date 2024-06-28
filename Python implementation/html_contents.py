def get_html(top_margin, table_name, col1_title, col2_title, **rows):
    rows = list(rows.items())
    element_html = f"""
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
    return element_html