from app_elements.page_elements import get_table
from dash import no_update
import copy

## COMMON CALLBACKS ##
def update_table(mode:str,
                 grouping_feature:str,
                 table_id:dict) -> list[dict]:
    """
    Updater della tabella di visualizzazione dei file.

    Nel caso venga richiesto il raggruppamento dei dati da parte dell selettore, ricrea la tabella, raggruppando gli
    esperimenti secondo la feature grouping_feature, e calcolando le medie delle affinità, se presenti. Nella colonna
    degli indirizzi verranno salvate degli indirizzi dei file che fanno parte del gruppo sotto forma di stringhe, divisi
    da cancelletti (#).
    """
    if mode == "grouped":
        df_out,cols_defs,_ = get_table(table_id, grouping_feat=grouping_feature)
    elif mode == "normal":
        df_out,cols_defs,_ = get_table(table_id)
    elif not mode:
        return no_update, no_update, no_update, no_update
    else:
        raise ValueError(f"Il valore passato dal radio selector [{mode}], non è tra quelli supportati")

    for col in cols_defs:
        if col['field']==grouping_feature:
            print(col)

    return df_out.to_dict('records'), cols_defs, [], None
