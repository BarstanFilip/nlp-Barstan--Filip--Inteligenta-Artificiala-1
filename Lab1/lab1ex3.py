import re as re
import unicodedata

#tokenizere
def tokenize_words(text: str):
    return text.split()

def tokenize_characters(text: str):
    text_no_spaces = text.replace(" ", "")
    return list(text_no_spaces)

#normalizare
def remove_diacritics(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")



#normalizare
def normalize(text: str):
    text = remove_diacritics(text)
    text = text.lower()
    text = re.sub(r"[^\w\s%/]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()
    return text


rl_medicale = {
    "febra": "Ai febră. Odihnește-te, hidratează-te și monitorizează temperatura. Dacă depășește 38.5°C sau durează mai mult de câteva zile, consultă medicul.",
    "tuse": "Tusea poate fi cauzată de o infecție respiratorie. Dacă apare cu febră mare sau dificultăți de respirație, mergi la medic.",
    "gat": "Durerea în gât poate fi virală sau bacteriană. Dacă devine intensă sau ai probleme la înghițire, cere sfatul unui medic.",
    "ameteli": "Amețelile pot fi din deshidratare sau tensiune scăzută. Dacă persistă, contactează un medic.",
    "greata": "Grețurile pot fi cauzate de indigestie sau alte afecțiuni. Dacă sunt severe, consultă medicul.",
    "durere abdominala": "Durerile abdominale pot avea multiple cauze. Dacă persistă sau sunt severe, mergi la urgențe.",
    "durere in piept": "Durerile în piept pot fi grave. Dacă sunt intense sau apăsătoare, sună imediat la 112.",
    "tensiune mica": "Tensiunea scăzută poate provoca slăbiciune și amețeli. Hidratează-te și consultă medicul dacă simptomele persistă.",
    "oxigen scazut": "Nivel scăzut de oxigen (sub ~94%) poate fi periculos. Dacă ai dificultăți de respirație, mergi la spital urgent.",
    "puls crescut": "Puls crescut poate apărea din cauza stresului, efortului sau problemelor cardiace. Dacă persistă la repaus, consultă medicul."
}


#detectarea oxigen si puls
def detect_oxygen(text: str):
    match = re.search(r"(\d{2,3})%", text)
    if match:
        value = int(match.group(1))
        if value < 94:
            return "oxigen scazut"
    return None

def detect_pulse(text: str):
    match_hr = re.search(r"hr\s*(\d{2,3})", text)
    if match_hr:
        value = int(match_hr.group(1))
        if value >= 100:
            return "puls crescut"
    match_puls = re.search(r"puls\w*\s*(este\s*)?(\d{2,3})", text)
    if match_puls:
        value = int(match_puls.group(2))
        if value >= 100:
            return "puls crescut"
    return None


def chatbot(user_input: str) -> str:
    normalizare = normalize(user_input)
    
    #tokenizare
    word_tokens = tokenize_words(normalizare)
    char_tokens = tokenize_characters(normalizare)


    print("\n///////TASKURI//////")
    print("Normalizare ", normalizare)
    print("Tokenizare pe cuvinte ", word_tokens)
    print("Tokenizare pe caracterer ", char_tokens)
    print("\n")
    
    #valori medicare oxigen/puls
    o2_rule = detect_oxygen(normalizare)
    pulse_rule = detect_pulse(normalizare)
    
    for key in [o2_rule, pulse_rule]:
        if key and key in rl_medicale:
            return rl_medicale[key]
    
    if "tensiune" in normalizare and "mica" in normalizare:
        return rl_medicale["tensiune mica"]
    
    for key, value in rl_medicale.items():
        if key in normalizare:
            return value
        
    return "Nu inteleg itrebarea"

a = True

print("///////////////Chatbot/////////////////////")
while a:
    user_input = input("ask a question  ")
    reply = chatbot(user_input)
    print(f"Chatbot->  {reply}")
    if user_input == "esc":
        a = False
