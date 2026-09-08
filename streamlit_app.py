import os
import requests
import streamlit as st


API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000",
)


def get_api_data(
    path: str,
    params: dict[str, str] | None = None,
) -> dict | list | None:
    try:
        response = requests.get(
            f"{API_URL}{path}",
            params=params,
            timeout=90,
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.Timeout:
        st.error("API neodpovědělo včas.")

    except requests.exceptions.ConnectionError:
        st.error(
            "Nepodařilo se připojit k FastAPI. "
            "Zkontrolujte, zda server běží."
        )

    except requests.exceptions.HTTPError as error:
        status_code = None
        detail = "Neznámá chyba."

        if error.response is not None:
            status_code = error.response.status_code

            try:
                error_data = error.response.json()
                detail = error_data.get(
                    "detail",
                    detail,
                )
            except requests.exceptions.JSONDecodeError:
                pass

        st.error(
            f"API vrátilo chybu "
            f"{status_code or 'neznámého typu'}: "
            f"{detail}"
        )

    return None


st.set_page_config(
    page_title="Board Game Search",
    page_icon="🎲",
)

st.title("Vyhledávání deskových her")

if "games" not in st.session_state:
    st.session_state.games = []

if "game_detail" not in st.session_state:
    st.session_state.game_detail = None

query = st.text_input(
    "Zadejte název hry nebo rozšíření:",
    placeholder="Například Catan",
)

if st.button("Vyhledat"):
    if not query.strip():
        st.warning("Zadejte název hry.")

    else:
        with st.spinner("Vyhledávám hry..."):
            search_results = get_api_data(
                "/games",
                params={"query": query.strip()},
            )

        if search_results is not None:
            st.session_state.games = search_results
            st.session_state.game_detail = None

games = st.session_state.games

if games:
    st.success(
        f"Počet nalezených výsledků: {len(games)}"
    )

    st.dataframe(
        games,
        width="stretch",
        hide_index=True,
    )

    game_by_id = {
        game["id"]: game
        for game in games
    }

    selected_game_id = st.selectbox(
        "Vyberte hru:",
        options=list(game_by_id),
        format_func=lambda game_id: (
            f"{game_by_id[game_id]['name']} "
            f"({game_by_id[game_id]['year_published'] or 'rok neuveden'})"
        ),
    )

    current_detail = st.session_state.game_detail

    if (
        current_detail is not None
        and current_detail["id"] != selected_game_id
    ):
        st.session_state.game_detail = None

    if st.button("Zobrazit detail"):
        with st.spinner("Načítám detail hry..."):
            detail = get_api_data(
                f"/games/{selected_game_id}"
            )

        if detail is not None:
            st.session_state.game_detail = detail

game_detail = st.session_state.game_detail

if game_detail is not None:
    st.subheader(game_detail["name"])

    image_url = game_detail.get("image_url")
    description = game_detail.get("description")

    if image_url:
        st.image(
            image_url,
            width=250,
        )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Rok vydání",
        game_detail["year_published"]
        or "Neuvedeno",
    )

    col2.metric(
        "Počet hráčů",
        (
            f"{game_detail['min_players']}–"
            f"{game_detail['max_players']}"
            if game_detail["min_players"] is not None
            and game_detail["max_players"] is not None
            else "Neuvedeno"
        ),
    )

    rating = game_detail.get("rating")

    col3.metric(
        "Hodnocení",
        (
            f"{rating:.2f}"
            if rating is not None
            else "Neuvedeno"
        ),
    )

    weight = game_detail.get("weight")

    col4.metric(
        "Obtížnost (1–5)",
        (
            f"{weight:.2f}"
            if weight is not None
            else "Neuvedeno"
        ),
    )

    if description:
        with st.expander("Zobrazit popis hry"):
            st.write(description)

    st.write(
        "**Autoři:**",
        ", ".join(game_detail["designers"])
        or "Neuvedeno",
    )

    st.write(
        "**Kategorie:**",
        ", ".join(game_detail["categories"])
        or "Neuvedeno",
    )

    st.write(
        "**Mechaniky:**",
        ", ".join(game_detail["mechanics"])
        or "Neuvedeno",
    )

    st.write(
        "**Vydavatelé:**",
        ", ".join(game_detail["publishers"])
        or "Neuvedeno",
    )