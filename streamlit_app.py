
import os
import json

import requests
import streamlit as st
import streamlit.components.v1 as components


API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
try:
    COPYWRITER_PASSWORD = st.secrets["COPYWRITER_PASSWORD"]
except (KeyError, FileNotFoundError):
    COPYWRITER_PASSWORD = os.getenv("COPYWRITER_PASSWORD", "")


st.set_page_config(
    page_title="Board Game Search",
    page_icon="🎲",
    layout="wide",
)


def get_api_data(endpoint, params=None):
    """Načte data z backendového API."""
    url = f"{API_URL.rstrip('/')}/{endpoint.lstrip('/')}"

    try:
        response = requests.get(
            url,
            params=params,
            timeout=90,
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        st.error("Požadavek trval příliš dlouho. Zkuste to prosím znovu.")

    except requests.exceptions.ConnectionError:
        st.error(
            "Nepodařilo se připojit k API. "
            "Zkontrolujte, zda backend běží."
        )

    except requests.exceptions.HTTPError as error:
        st.error(f"API vrátilo HTTP chybu: {error}")

    except requests.exceptions.RequestException as error:
        st.error(f"Chyba při komunikaci s API: {error}")

    except ValueError:
        st.error("API nevrátilo platná JSON data.")

    return None


def format_value(value, fallback="x"):
    """Převede hodnotu na text nebo vrátí náhradní hodnotu."""
    if value is None or value == "":
        return fallback

    return str(value)


def format_decimal(value):
    """Formátuje číslo s jedním desetinným místem a českou čárkou."""
    if value is None or value == "":
        return "x"

    try:
        return f"{float(value):.1f}".replace(".", ",")
    except (ValueError, TypeError):
        return str(value)


def format_players(game):
    """Vrátí počet hráčů ve formátu min–max."""
    minimum = game.get("min_players")
    maximum = game.get("max_players")

    if minimum is None or maximum is None:
        return "x"

    return f"{minimum}–{maximum}"


def format_dimensions(version):
    """Vrátí rozměry bez jednotek."""
    width = version.get("width")
    length = version.get("length")
    depth = version.get("depth")

    if width is None or length is None or depth is None:
        return "x"

    return f"{width} × {length} × {depth}"


def format_list(values):
    """Převede seznam hodnot na text."""
    if not values:
        return "x"

    if isinstance(values, str):
        return values

    return ", ".join(str(value) for value in values)


def get_game_list(data):
    """Podporuje seznam her i seznam zabalený v objektu JSON."""
    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in ("games", "results", "items"):
            if isinstance(data.get(key), list):
                return data[key]

    return []


def get_game_name(game):
    """Vrátí název hry."""
    return game.get("name") or game.get("title") or "Neznámá hra"


def get_version_name(version):
    """Vrátí název konkrétní edice."""
    return (
        version.get("name")
        or version.get("title")
        or version.get("product_name")
        or "Edice bez názvu"
    )


def get_version_language(version):
    """Vrátí jazyk edice, pokud je dostupný."""
    language = version.get("language")

    if isinstance(language, list):
        return ", ".join(str(item) for item in language)

    return language or ""


def get_default_language(version):
    """Navrhne jazyk CZ/EN podle údajů o konkrétní edici."""
    language = get_version_language(version).lower()

    if "czech" in language or "češt" in language or "cz" in language:
        return "CZ"

    if "english" in language or "anglič" in language or "en" in language:
        return "EN"

    return "x"


def get_version_weight(version):
    """Vrátí hmotnost edice v gramech."""
    weight = version.get("weight_g")

    if weight is None:
        return "x"

    return str(weight)


def get_version_id(version):
    """Vrátí ID edice pro identifikaci formuláře."""
    return (
        version.get("id")
        or version.get("version_id")
        or get_version_name(version)
    )


def render_copy_button(value, index):
    """Vykreslí tlačítko pro zkopírování hodnoty do schránky."""
    encoded_value = json.dumps(str(value), ensure_ascii=False)

    components.html(
        f"""
        <div style="text-align: right;">
            <button
                id="copy-{index}"
                style="
                    padding: 6px 12px;
                    border: 1px solid #888;
                    border-radius: 6px;
                    background: transparent;
                    cursor: pointer;
                    font-size: 13px;
                "
            >
                Uložit do schránky
            </button>
        </div>

        <script>
        const button = document.getElementById("copy-{index}");

        button.addEventListener("click", async () => {{
            try {{
                await navigator.clipboard.writeText({encoded_value});
                button.textContent = "Zkopírováno ✓";
            }} catch (error) {{
                button.textContent = "Kopírování selhalo";
            }}
        }});
        </script>
        """,
        height=42,
    )


def render_copywriter_field(
    label,
    value,
    index,
    warning=None,
    warning_color="red",
    instruction=None,
    multiline=False,
    height=100,
    key=None,
    link=None,
):
    """Vykreslí popisek, instrukci, editační pole a kopírovací tlačítko."""
    st.markdown(
        f"**{label}**"
        + (
            f" <span style='color:{warning_color}'>{warning}</span>"
            if warning
            else ""
        ),
        unsafe_allow_html=True,
    )

    if instruction:
        st.caption(instruction)

    if link:
        st.markdown(link)

    if multiline:
        value = st.text_area(
            label,
            value=value,
            height=height,
            key=key,
            label_visibility="collapsed",
        )
    else:
        value = st.text_input(
            label,
            value=value,
            key=key,
            label_visibility="collapsed",
        )

    render_copy_button(value, index)

    return value


DESCRIPTION_TEMPLATE = (
    "1. Shrnutí (1–2 věty)\n"
    "Podstatné informace o hře a jeden hlavní benefit. "
    "Bez superlativů.\n\n"
    "2. Klíčové vlastnosti a benefity (3–5 bodů)\n"
    "• **Vlastnost:** Přínos pro hráče.\n"
    "• **Vlastnost:** Přínos pro hráče.\n"
    "• **Vlastnost:** Přínos pro hráče.\n"
    "U rozšíření uveďte rozšíření jako první.\n\n"
    "3. Emotivní / narativní popis\n"
    "Krátký atmosférický text s krátkými větami.\n"
    "Produkt C: 20–40 slov | B: 40–80 slov | A: 80–150 slov\n\n"
    "4. Obsah balení\n"
    "• ...\n\n"
    "5. Další nezbytné informace\n"
    "Uveďte pouze tehdy, pokud jsou důležité."
)


# --------------------------------------------------
# Výběr režimu a ochrana heslem
# --------------------------------------------------

st.title("🎲 Board Game Search")

mode_column, password_column, button_column = st.columns([1.2, 1, 0.55])

with mode_column:
    mode = st.radio(
        "Režim",
        ["PRO HRÁČE", "PRO COPYWRITERY"],
        horizontal=True,
    )

if mode == "PRO COPYWRITERY":
    with password_column:
        entered_password = st.text_input(
            "Heslo pro copywritery",
            type="password",
            key="copywriter_password_input",
            placeholder="Zadejte heslo",
        )

    with button_column:
        st.write("")
        unlock_clicked = st.button(
            "Odemknout",
            type="primary",
            use_container_width=True,
        )

    if not COPYWRITER_PASSWORD:
        st.error(
            "Heslo není nastavené. "
            "Nastavte proměnnou prostředí COPYWRITER_PASSWORD."
        )
        st.stop()

    if unlock_clicked:
        if entered_password == COPYWRITER_PASSWORD:
            st.session_state["copywriter_authenticated"] = True
            st.rerun()
        else:
            st.session_state["copywriter_authenticated"] = False
            st.error("Nesprávné heslo.")

    if not st.session_state.get("copywriter_authenticated", False):
        st.stop()

else:
    # Po návratu do režimu pro hráče bude při dalším výběru
    # režimu pro copywritery nutné heslo zadat znovu.
    st.session_state["copywriter_authenticated"] = False


# --------------------------------------------------
# Vyhledávání her
# Tato část se vykreslí až po ověření hesla,
# pokud je zvolen režim PRO COPYWRITERY.
# --------------------------------------------------

st.divider()

query = st.text_input(
    "Vyhledat deskovou hru",
    placeholder="Zadejte název hry, například Catan",
)

if st.button("Vyhledat", type="primary"):
    if query.strip():
        st.session_state["search_results"] = None
        st.session_state["selected_game_id"] = None

        search_data = get_api_data(
            "/games",
            params={"query": query.strip()},
        )

        if search_data is not None:
            st.session_state["search_results"] = get_game_list(search_data)

    else:
        st.warning("Nejprve zadejte název hry.")


search_results = st.session_state.get("search_results")

if search_results is not None:
    if not search_results:
        st.info("Nebyly nalezeny žádné hry.")

    else:
        table_rows = []

        for game in search_results:
            table_rows.append(
                {
                    "ID": game.get("id"),
                    "Název": get_game_name(game),
                    "Rok vydání": game.get("year", "x"),
                }
            )

        st.subheader("Výsledky vyhledávání")
        st.dataframe(
            table_rows,
            use_container_width=True,
            hide_index=True,
        )

        game_options = {
            f"{get_game_name(game)} ({game.get('year', 'x')}) — ID {game.get('id')}":
                game.get("id")
            for game in search_results
            if game.get("id") is not None
        }

        if game_options:
            selected_label = st.selectbox(
                "Vyberte hru",
                options=list(game_options.keys()),
            )

            if st.button("Zobrazit detail"):
                st.session_state["selected_game_id"] = game_options[
                    selected_label
                ]
                st.session_state.pop("game_detail", None)


# --------------------------------------------------
# Detail hry
# --------------------------------------------------

selected_game_id = st.session_state.get("selected_game_id")

if selected_game_id is not None:
    if (
        "game_detail" not in st.session_state
        or st.session_state.get("loaded_game_id") != selected_game_id
    ):
        detail_data = get_api_data(f"/games/{selected_game_id}")

        if detail_data is not None:
            st.session_state["game_detail"] = detail_data
            st.session_state["loaded_game_id"] = selected_game_id

    game_detail = st.session_state.get("game_detail")

    if game_detail:
        st.divider()
        st.header(get_game_name(game_detail))

        # ------------------------------------------
        # Režim pro hráče
        # ------------------------------------------

        if mode == "PRO HRÁČE":
            image_url = (
                game_detail.get("image")
                or game_detail.get("image_url")
                or game_detail.get("thumbnail")
            )

            if image_url:
                st.image(image_url, width=300)

            col1, col2 = st.columns(2)

            with col1:
                st.write(
                    "**Rok vydání:**",
                    format_value(game_detail.get("year")),
                )
                st.write(
                    "**Počet hráčů:**",
                    format_players(game_detail),
                )
                st.write(
                    "**Délka hry:**",
                    format_value(game_detail.get("playing_time")),
                )
                st.write(
                    "**Minimální věk:**",
                    format_value(game_detail.get("min_age")),
                )

            with col2:
                st.write(
                    "**Hodnocení BGG:**",
                    format_decimal(game_detail.get("rating")),
                )
                st.write(
                    "**Obtížnost:**",
                    format_decimal(game_detail.get("weight")),
                )

            description = game_detail.get("description")

            if description:
                with st.expander("Popis hry"):
                    st.write(description)

            st.subheader("Autoři")
            st.write(format_list(game_detail.get("designers")))

            st.subheader("Kategorie")
            st.write(format_list(game_detail.get("categories")))

            st.subheader("Herní mechanismy")
            st.write(format_list(game_detail.get("mechanics")))

            st.subheader("Vydavatelé")
            st.write(format_list(game_detail.get("publishers")))

        # ------------------------------------------
        # Režim pro copywritery
        # ------------------------------------------

        else:
            versions = game_detail.get("versions") or []

            if not versions:
                st.warning(
                    "Pro tuto hru nejsou k dispozici žádné edice. "
                    "Údaje o konkrétním vydání bude potřeba ověřit ručně."
                )

            else:
                version_labels = [
                    f"{get_version_name(version)} "
                    f"(ID: {get_version_id(version)})"
                    for version in versions
                ]

                default_version_index = next(
                    (
                        index
                        for index, version in enumerate(versions)
                        if (
                            "czech" in get_version_language(version).lower()
                            or "češt" in get_version_language(version).lower()
                            or "cz" in get_version_language(version).lower()
                        )
                    ),
                    0,
                )

                selected_version_label = st.selectbox(
                    "Vyberte konkrétní edici",
                    options=version_labels,
                    index=default_version_index,
                    key=f"version_select_{game_detail.get('id')}",
                )

                selected_version_index = version_labels.index(
                    selected_version_label
                )
                selected_version = versions[selected_version_index]
                selected_version_id = get_version_id(selected_version)

                st.caption(
                    "Zkontrolujte, zda vybraná edice odpovídá "
                    "produktu prodávanému v e-shopu."
                )

                st.divider()
                st.subheader("Texty pro e-shop")

                warning_labels = {
                    "Nový název": "- potřeba upravit!",
                    "Meta title": "- potřeba upravit!",
                    "Meta description": "- potřeba upravit!",
                    "Popis (nový)": "- potřeba upravit!",
                    "BG: Herní rodina": "- potřeba upravit!",
                }

                selection_labels = {
                    "Jazyk": "- potřeba vybrat z nabídky",
                    "BG: Herní principy": "- potřeba vybrat z nabídky",
                    "BG: Podkategorie": "- potřeba vybrat z nabídky",
                }

                missing_data_labels = {
                    "Váha v gramech": '- pokud na BGG chybí, vložíš "x"',
                    "Rozměr": '- pokud na BGG chybí, vložíš "x"',
                }

                instructions = {
                    "Nový název": (
                        "Oficiální název hry (pokud nutné, doplňte o stručné upřesnění). "
                        "Max. 40 znaků, pokud to délka oficiálního názvu dovoluje."
                    ),
                    "Meta title": (
                        "Pro vyhledávače. Název hry doplňte o označení "
                        "„desková hra“, „karetní hra“ nebo vhodnou podkategorii. "
                        "Max. 55 znaků."
                    ),
                    "Meta description": (
                        "Musí obsahovat název hry, nejsilnější benefit "
                        "a slova „desková hra“ nebo „karetní hra“. Max. 160 znaků."
                    ),
                    "Popis (nový)": (
                        "Vytvořte popis podle Tone of Voice Černého rytíře."
                    ),
                    "Jazyk": (
                        "Ověřte jazyk skutečné edice prodávané v e-shopu. "
                        "Vyplňte CZ nebo EN."
                    ),
                    "BG: Herní principy": (
                        "Pokud se jedná o nový (neznámý) mechanismus, zadejte x. "
                        "Názvy mechanismů (např. deckbuilding) nepřekládejte."
                    ),
                    "BG: Herní rodina": (
                        "Uveďte sérii nebo herní systém. U rozšíření uveďte "
                        "základní hru. U samostatné hry ponechte její název. "
                        "Zadejte v odpovídajícím jazyce (nejčastěji CZ)."
                    ),
                    "BG: Podkategorie": (
                        "Vyberte 1–3 kategorie relevantní pro e-shop: "
                        "Rodinné hry, Dětské hry, Párty hry, Hry pro dva, "
                        "Únikové a detektivní, Pro náročné hráče, "
                        "Karetní hry nebo Kooperativní hry."
                    ),
                }

                tone_of_voice_link = (
                    "[Otevřít Tone of Voice Černého rytíře]"
                    "(https://app.notion.com/p/"
                    "Tone-of-voice-28d62c5d3ad780399b91e761d9207e97)"
                )

                field_prefix = (
                    f"copywriter_{game_detail.get('id')}_"
                    f"{selected_version_id}"
                )

                fields = [
                    ("Nový název", get_game_name(game_detail), False),
                    ("Meta title", "x", False),
                    ("Meta description", "x", False),
                    ("Popis (nový)", DESCRIPTION_TEMPLATE, True),
                    ("Jazyk", get_default_language(selected_version), False),
                    ("Váha v gramech", get_version_weight(selected_version), False),
                    ("Rozměr", format_dimensions(selected_version), False),
                    ("BG: BGG hodnocení", format_decimal(game_detail.get("rating")), False),
                    ("BG: Herní principy", format_list(game_detail.get("mechanics")), False),
                    ("BG: Délka hry (min)", format_value(game_detail.get("playing_time")), False),
                    ("BG: Herní rodina", get_game_name(game_detail), False),
                    ("BG: Minimální věk hráčů", format_value(game_detail.get("min_age")), False),
                    ("BG: Obtížnost", format_decimal(game_detail.get("weight")), False),
                    ("BG: Podkategorie", format_list(game_detail.get("categories")), False),
                    ("BG: Počet hráčů", format_players(game_detail), False),
                ]

                for index, (label, default_value, multiline) in enumerate(fields):
                    if label in warning_labels:
                        warning = warning_labels[label]
                        warning_color = "red"
                    elif label in selection_labels:
                        warning = selection_labels[label]
                        warning_color = "red"
                    elif label in missing_data_labels:
                        warning = missing_data_labels[label]
                        warning_color = "black"
                    else:
                        warning = "- netřeba upravovat"
                        warning_color = "black"

                    instruction = instructions.get(label)
                    link = (
                        tone_of_voice_link
                        if label == "Popis (nový)"
                        else None
                    )

                    field_key = f"{field_prefix}_{index}"

                    render_copywriter_field(
                        label=label,
                        value=default_value,
                        index=index,
                        warning=warning,
                        warning_color=warning_color,
                        instruction=instruction,
                        multiline=multiline,
                        height=350 if label == "Popis (nový)" else 100,
                        key=field_key,
                        link=link,
                    )
