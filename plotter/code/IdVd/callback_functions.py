from pathlib import Path
import plotly.io as pio
from dash import dcc
from plotter.code.common import *
from .parameters import df, exp_mode_dict, group_mode_dict

## CALLBACKS FUNCTIONS ##
def update_tabs(n_clicks, curr_mode, selected_rows, table_data, curr_tab, tabs):
    labels = {'exponential':'exp', 'gaussian':'gauss', 'uniform':'unif'}
    tabs = tabs or []
    if not n_clicks or not selected_rows:
        return tabs,[],curr_tab

    open_tabs = [tab['props']['value'] for tab in tabs]

    for selected_index in selected_rows:
        row = table_data[selected_index]
        if curr_mode == 'Exp mode':
            file = row['file_path']
            if file not in open_tabs:
                tabs.append(
                    dcc.Tab(
                        label=f"Exp - {labels[row['trap_distr']]}/{row['e_mid']}/{row['e_sigma']}/{row['v_gf']}",
                        value=file
                    )
                )
        else:
            group = row['group']
            if group not in open_tabs:
                tabs.append(
                    dcc.Tab(
                        label=f"Group - {labels[row['trap_distr']]}/{row['e_mid']}/{row['e_sigma']}",
                        value=group
                    )
                )

    if not open_tabs:
        if curr_mode == 'Exp mode':
            return tabs,[],table_data[selected_rows[0]]['file_path']    # se non c'è alcun tab già aperto, apro il primo tab
        else:
            return tabs,[],table_data[selected_rows[0]]['group']
    else:
        return tabs,[],curr_tab     # altrimenti lascio aperto il tab già selezionato

def update_graph_content(tab, checked_curves):
    if not tab:
        return "nulla di selezionato"
    if '.csv' not in tab:
        df_group = df.loc[df['group']==tab]
        g = ExpCurves(*df_group['file_path']).import_data()
        return dcc.Graph(figure=plot(g,checked_curves))
    else:
        e = ExpCurves(tab).import_data()
        return dcc.Graph(figure=plot(e,checked_curves))

def update_table(mode):
    if mode == 'Exp mode':
        return exp_mode_dict,['file_path', 'group'],[]
    else:
        return group_mode_dict,['file_path', 'group', 'v_gf'],[]

def export_selected(n_clicks, mode, selected_curves, selected_rows, data_table):     # AGGIUNGERE BOX PER SCELTA DOWNLOAD_PATH, ESTENSIONE, CURVE DA PLOTTARE
    if not n_clicks or not selected_rows:
        return selected_rows
    export_path = find_export_path()
    figs,exp_file_paths = [],[]
    match mode:
        case 'Exp mode':
            exps:list[ExpCurves] = [ExpCurves(data_table[row_i]['file_path']).import_data() for row_i in selected_rows]   # lista di esperimenti corrispondente alle righe selezionate
            figs:list[go.Figure] = [plot(exp,selected_curves) for exp in exps]
            exp_file_paths:list[Path] = [export_path/Path(f"{exp}.png") for exp in exps]  #estensioni possibili .png, .svg, .pdf
        case 'Group mode':
            groups_files:list[list[str]] = [df.loc[df.group==data_table[row_i]['group']]['file_path'].tolist() for row_i in selected_rows]  # lista contenente liste di indirizzi di file appartenenti ai gruppi selezionati
            groups_curves:list[ExpCurves] = [ExpCurves(*group_files).import_data() for group_files in groups_files]
            figs:list[go.Figure] = [plot(group_curves,selected_curves) for group_curves in groups_curves]
            exp_file_paths:list[Path] = [export_path/Path(f"{group_curves}.png") for group_curves in groups_curves]
    pio.write_images(
        fig=figs,
        file=exp_file_paths
    )
    return False

def toggle_modal(n_clicks, is_open):
    if not n_clicks:
        return is_open
    return not is_open

## HELPER FUNC ##
def try_mkdir(path:Path)->Path:
    """
    Prova a creare la directory specificata
    :param path: indirizzo della directory da creare
    :type path: pathlib.Path
    :return: l'indirizzo della directory creata o None nel caso esistesse già
    :rtype: pathlib.Path or None
    :raises RuntimeError: Nel caso fosse impossibile creare la directory specificata
    """
    try:
        path.mkdir(parents=True)
    except FileExistsError:
        return None
    except:
        raise RuntimeError(f"Impossibile creare {path}")
    return path

def find_export_path()->Path:
    """
    Crea un indirizzo di esportazione valido
    :return: Indirizzo di esportazione creato
    :rtype: pathlib.Path
    """
    i=0
    while True:
        export_path = try_mkdir(Path("../../exported_files/export" if i==0 else f"../../exported_files/export-{i}"))
        if export_path:
          return export_path
        i+=1