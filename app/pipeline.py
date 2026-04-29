from app.analysis_graph import ANALYSIS_GRAPH


def run_analysis(dataframe, dataset_name: str, show_execution_order: bool = False) -> bytes:
    final_state = ANALYSIS_GRAPH.invoke(
        {
            "dataset_name": dataset_name,
            "raw_df": dataframe,
            "show_execution_order": show_execution_order,
            "insight_ledger": [],
            "accepted_count": 0,
            "function_calls": 0,
            "specialist_request_signatures": [],
            "stop": False,
        }
    )
    return final_state["pdf_bytes"]
