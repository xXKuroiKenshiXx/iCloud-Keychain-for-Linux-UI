"""Interface translations. English strings are the keys; a missing entry falls back to
English. `{name}` placeholders are filled by the caller after translation."""

from __future__ import annotations

LANGUAGES = {
    "en": "English",
    "es": "Español",
    "pt": "Português",
    "fr": "Français",
    "de": "Deutsch",
    "it": "Italiano",
}

_T = {
    # ---- window, sidebar, list
    "Passwords": ("Contraseñas", "Senhas", "Mots de passe", "Passwörter", "Password"),
    "Search": ("Buscar", "Pesquisar", "Rechercher", "Suchen", "Cerca"),
    "All": ("Todas", "Todas", "Tous", "Alle", "Tutte"),
    "Codes": ("Códigos", "Códigos", "Codes", "Codes", "Codici"),
    "Wi-Fi": ("Wi-Fi", "Wi-Fi", "Wi-Fi", "WLAN", "Wi-Fi"),
    "Apple Account": ("Cuenta de Apple", "Conta Apple", "Compte Apple", "Apple Account", "Account Apple"),
    "Sign In": ("Iniciar sesión", "Iniciar sessão", "Se connecter", "Anmelden", "Accedi"),
    "Working…": ("Trabajando…", "Trabalhando…", "En cours…", "Wird ausgeführt…", "In corso…"),
    "Settings": ("Ajustes", "Ajustes", "Réglages", "Einstellungen", "Impostazioni"),
    "All Passwords": ("Todas las contraseñas", "Todas as senhas", "Tous les mots de passe", "Alle Passwörter", "Tutte le password"),
    "Syncing": ("Sincronizando", "Sincronizando", "Synchronisation", "Synchronisiert", "Sincronizzazione"),
    "Sync": ("Sincronizar", "Sincronizar", "Synchroniser", "Synchronisieren", "Sincronizza"),
    "No user name": ("Sin usuario", "Sem nome de utilizador", "Aucun nom d’utilisateur", "Kein Benutzername", "Nessun nome utente"),
    "No results for “{q}”": ("No hay resultados para «{q}»", "Sem resultados para “{q}”", "Aucun résultat pour « {q} »", "Keine Ergebnisse für „{q}“", "Nessun risultato per «{q}»"),
    "Nothing here yet": ("Todavía no hay nada aquí", "Ainda não há nada aqui", "Rien pour l’instant", "Noch nichts hier", "Ancora niente qui"),
    # ---- detail
    "Choose an icon": ("Elegir un ícono", "Escolher um ícone", "Choisir une icône", "Symbol auswählen", "Scegli un’icona"),
    "Images": ("Imágenes", "Imagens", "Images", "Bilder", "Immagini"),
    "Select a password": ("Elige una contraseña", "Selecione uma senha", "Sélectionnez un mot de passe", "Passwort auswählen", "Seleziona una password"),
    "{n} passwords in your iCloud Keychain": ("{n} contraseñas en tu llavero de iCloud", "{n} senhas no seu Porta-chaves do iCloud", "{n} mots de passe dans votre trousseau iCloud", "{n} Passwörter in deinem iCloud-Schlüsselbund", "{n} password nel tuo portachiavi iCloud"),
    "Change Icon…": ("Cambiar ícono…", "Alterar ícone…", "Changer l’icône…", "Symbol ändern …", "Cambia icona…"),
    "Reset Icon": ("Restablecer ícono", "Repor ícone", "Réinitialiser l’icône", "Symbol zurücksetzen", "Ripristina icona"),
    "Shared group · {g}": ("Grupo compartido · {g}", "Grupo partilhado · {g}", "Groupe partagé · {g}", "Geteilte Gruppe · {g}", "Gruppo condiviso · {g}"),
    "User name": ("Usuario", "Nome de utilizador", "Nom d’utilisateur", "Benutzername", "Nome utente"),
    "Password": ("Contraseña", "Senha", "Mot de passe", "Passwort", "Password"),
    "Verification code": ("Código de verificación", "Código de verificação", "Code de validation", "Bestätigungscode", "Codice di verifica"),
    "Website": ("Sitio web", "Site", "Site web", "Website", "Sito web"),
    "Notes": ("Notas", "Notas", "Notes", "Notizen", "Note"),
    "Copy": ("Copiar", "Copiar", "Copier", "Kopieren", "Copia"),
    # ---- settings
    "Anisette service": ("Servicio de anisette", "Serviço anisette", "Service anisette", "Anisette-Dienst", "Servizio anisette"),
    "Session and vault": ("Sesión y bóveda", "Sessão e cofre", "Session et coffre", "Sitzung und Tresor", "Sessione e cassaforte"),
    "Website icons and names": ("Íconos y nombres de sitios", "Ícones e nomes de sites", "Icônes et noms des sites", "Website-Symbole und -Namen", "Icone e nomi dei siti"),
    "Fetched directly from each saved site over HTTPS, never through an icon service, and stored encrypted on this computer.": (
        "Se descargan directo de cada sitio guardado por HTTPS, nunca a través de un servicio de íconos, y se guardan cifrados en esta computadora.",
        "Obtidos diretamente de cada site guardado via HTTPS, nunca através de um serviço de ícones, e guardados encriptados neste computador.",
        "Récupérées directement depuis chaque site enregistré en HTTPS, jamais via un service d’icônes, et stockées chiffrées sur cet ordinateur.",
        "Direkt per HTTPS von jeder gespeicherten Website geladen, nie über einen Symboldienst, und verschlüsselt auf diesem Computer gespeichert.",
        "Scaricate direttamente da ogni sito salvato tramite HTTPS, mai tramite un servizio di icone, e salvate cifrate su questo computer."),
    "Refresh": ("Actualizar", "Atualizar", "Actualiser", "Aktualisieren", "Aggiorna"),
    "Status": ("Estado", "Estado", "État", "Status", "Stato"),
    "Signed in · {n} passwords": ("Sesión iniciada · {n} contraseñas", "Sessão iniciada · {n} senhas", "Connecté · {n} mots de passe", "Angemeldet · {n} Passwörter", "Accesso eseguito · {n} password"),
    "Not signed in": ("Sin sesión iniciada", "Sem sessão iniciada", "Non connecté", "Nicht angemeldet", "Accesso non eseguito"),
    "Language": ("Idioma", "Idioma", "Langue", "Sprache", "Lingua"),
    "System ({lang})": ("Sistema ({lang})", "Sistema ({lang})", "Système ({lang})", "System ({lang})", "Sistema ({lang})"),
    "Debug console": ("Consola de depuración", "Consola de depuração", "Console de débogage", "Debug-Konsole", "Console di debug"),
    "Following": ("Siguiendo", "A seguir", "Suivi actif", "Folgt", "Segue"),
    "Follow": ("Seguir", "Seguir", "Suivre", "Folgen", "Segui"),
    "Copy Log": ("Copiar registro", "Copiar registo", "Copier le journal", "Protokoll kopieren", "Copia registro"),
    "Clear": ("Limpiar", "Limpar", "Effacer", "Leeren", "Cancella"),
    "Engine activity appears here step by step.": ("La actividad del motor aparece aquí paso a paso.", "A atividade do motor aparece aqui passo a passo.", "L’activité du moteur s’affiche ici étape par étape.", "Die Aktivität der Engine erscheint hier Schritt für Schritt.", "L’attività del motore compare qui passo dopo passo."),
    # ---- sign-in
    "Account": ("Cuenta", "Conta", "Compte", "Account", "Account"),
    "Code": ("Código", "Código", "Code", "Code", "Codice"),
    "Device": ("Dispositivo", "Dispositivo", "Appareil", "Gerät", "Dispositivo"),
    "Passcode": ("Código de desbloqueo", "Código", "Code d’accès", "Gerätecode", "Codice"),
    "Sign in with your Apple Account": ("Inicia sesión con tu cuenta de Apple", "Inicie sessão com a sua Conta Apple", "Connectez-vous avec votre compte Apple", "Mit deinem Apple Account anmelden", "Accedi con il tuo Account Apple"),
    "Connecting to iCloud": ("Conectando con iCloud", "A ligar ao iCloud", "Connexion à iCloud", "Verbindung mit iCloud", "Connessione a iCloud"),
    "Enter the verification code": ("Ingresa el código de verificación", "Introduza o código de verificação", "Saisissez le code de validation", "Bestätigungscode eingeben", "Inserisci il codice di verifica"),
    "Choose a trusted device": ("Elige un dispositivo de confianza", "Escolha um dispositivo de confiança", "Choisissez un appareil de confiance", "Vertrauenswürdiges Gerät wählen", "Scegli un dispositivo attendibile"),
    "Join iCloud Keychain": ("Unirse al llavero de iCloud", "Aderir ao Porta-chaves do iCloud", "Rejoindre le trousseau iCloud", "iCloud-Schlüsselbund beitreten", "Unisciti al portachiavi iCloud"),
    "Enter the device passcode": ("Ingresa el código de desbloqueo", "Introduza o código do dispositivo", "Saisissez le code de l’appareil", "Gerätecode eingeben", "Inserisci il codice del dispositivo"),
    "iCloud Keychain is connected": ("El llavero de iCloud está conectado", "O Porta-chaves do iCloud está ligado", "Le trousseau iCloud est connecté", "iCloud-Schlüsselbund ist verbunden", "Il portachiavi iCloud è connesso"),
    "Enter your password": ("Ingresa tu contraseña", "Introduza a sua senha", "Saisissez votre mot de passe", "Passwort eingeben", "Inserisci la password"),
    "Apple needs an answer": ("Apple necesita una respuesta", "A Apple precisa de uma resposta", "Apple attend une réponse", "Apple benötigt eine Antwort", "Apple ha bisogno di una risposta"),
    "This computer joins your iCloud Keychain as a new device. Your password is sent only to Apple and is never shown or logged.": (
        "Esta computadora se une a tu llavero de iCloud como un dispositivo nuevo. Tu contraseña solo se envía a Apple y nunca se muestra ni se registra.",
        "Este computador junta-se ao seu Porta-chaves do iCloud como um novo dispositivo. A sua senha só é enviada à Apple e nunca é mostrada nem registada.",
        "Cet ordinateur rejoint votre trousseau iCloud comme nouvel appareil. Votre mot de passe n’est envoyé qu’à Apple et n’est jamais affiché ni journalisé.",
        "Dieser Computer tritt deinem iCloud-Schlüsselbund als neues Gerät bei. Dein Passwort wird nur an Apple gesendet und nie angezeigt oder protokolliert.",
        "Questo computer si unisce al tuo portachiavi iCloud come nuovo dispositivo. La password viene inviata solo ad Apple e non viene mai mostrata né registrata."),
    "Apple just showed a six-digit code on your iPhone, iPad or Mac. If it first asks to Allow a sign-in, tap Allow.": (
        "Apple acaba de mostrar un código de seis dígitos en tu iPhone, iPad o Mac. Si primero te pide permitir el inicio de sesión, toca Permitir.",
        "A Apple acabou de mostrar um código de seis dígitos no seu iPhone, iPad ou Mac. Se primeiro pedir para permitir o início de sessão, toque em Permitir.",
        "Apple vient d’afficher un code à six chiffres sur votre iPhone, iPad ou Mac. S’il demande d’abord d’autoriser la connexion, touchez Autoriser.",
        "Apple hat gerade einen sechsstelligen Code auf deinem iPhone, iPad oder Mac angezeigt. Wenn zuerst nach dem Erlauben gefragt wird, tippe auf „Erlauben“.",
        "Apple ha appena mostrato un codice a sei cifre su iPhone, iPad o Mac. Se prima chiede di consentire l’accesso, tocca Consenti."),
    "Pick the device whose screen passcode you know. Its passcode is what lets this computer read your passwords.": (
        "Elige el dispositivo cuyo código de desbloqueo conoces. Ese código es lo que permite a esta computadora leer tus contraseñas.",
        "Escolha o dispositivo cujo código de desbloqueio conhece. É esse código que permite a este computador ler as suas senhas.",
        "Choisissez l’appareil dont vous connaissez le code de déverrouillage. C’est ce code qui permet à cet ordinateur de lire vos mots de passe.",
        "Wähle das Gerät, dessen Code zum Entsperren du kennst. Mit diesem Code kann dieser Computer deine Passwörter lesen.",
        "Scegli il dispositivo di cui conosci il codice di sblocco. È quel codice che permette a questo computer di leggere le password."),
    "Next you'll type the screen passcode of {device}.": ("A continuación escribirás el código de desbloqueo de {device}.", "A seguir vai escrever o código de desbloqueio de {device}.", "Vous allez ensuite saisir le code de déverrouillage de {device}.", "Als Nächstes gibst du den Code zum Entsperren von {device} ein.", "Ora inserirai il codice di sblocco di {device}."),
    "The passcode you use to unlock {device}, not your Apple Account password and not the six-digit code.": (
        "El código que usas para desbloquear {device}; no es la contraseña de tu cuenta de Apple ni el código de seis dígitos.",
        "O código que usa para desbloquear {device}; não é a senha da Conta Apple nem o código de seis dígitos.",
        "Le code que vous utilisez pour déverrouiller {device}, ni le mot de passe de votre compte Apple ni le code à six chiffres.",
        "Der Code, mit dem du {device} entsperrst, nicht dein Apple Account-Passwort und nicht der sechsstellige Code.",
        "Il codice che usi per sbloccare {device}, non la password dell’Account Apple né il codice a sei cifre."),
    "that device": ("ese dispositivo", "esse dispositivo", "cet appareil", "dieses Gerät", "quel dispositivo"),
    "{n} passwords are now on this computer, encrypted.": ("Ahora hay {n} contraseñas en esta computadora, cifradas.", "Há agora {n} senhas neste computador, encriptadas.", "{n} mots de passe sont maintenant sur cet ordinateur, chiffrés.", "{n} Passwörter sind jetzt verschlüsselt auf diesem Computer.", "Ora ci sono {n} password su questo computer, cifrate."),
    "Your Apple Account password.": ("La contraseña de tu cuenta de Apple.", "A senha da sua Conta Apple.", "Le mot de passe de votre compte Apple.", "Das Passwort deines Apple Accounts.", "La password del tuo Account Apple."),
    "Your Apple Account email.": ("El correo de tu cuenta de Apple.", "O e-mail da sua Conta Apple.", "L’adresse e-mail de votre compte Apple.", "Die E-Mail-Adresse deines Apple Accounts.", "L’e-mail del tuo Account Apple."),
    "The anisette service at {url} isn't answering. Sign-in needs it: start it, then press Check Again.": (
        "El servicio de anisette en {url} no responde. Es necesario para iniciar sesión: inícialo y presiona Volver a comprobar.",
        "O serviço anisette em {url} não responde. É necessário para iniciar sessão: inicie-o e prima Verificar de novo.",
        "Le service anisette à {url} ne répond pas. Il est nécessaire pour se connecter : démarrez-le puis appuyez sur Vérifier à nouveau.",
        "Der Anisette-Dienst unter {url} antwortet nicht. Er wird zur Anmeldung benötigt: Starte ihn und tippe dann auf „Erneut prüfen“.",
        "Il servizio anisette su {url} non risponde. Serve per accedere: avvialo e premi Controlla di nuovo."),
    "Check Again": ("Volver a comprobar", "Verificar de novo", "Vérifier à nouveau", "Erneut prüfen", "Controlla di nuovo"),
    "No code? Unlock one of your Apple devices and wait a minute with this window open. Asking for codes repeatedly can block sign-in for a while.": (
        "¿No llega el código? Desbloquea uno de tus dispositivos Apple y espera un minuto con esta ventana abierta. Pedir códigos una y otra vez puede bloquear el inicio de sesión por un tiempo.",
        "Não recebeu o código? Desbloqueie um dos seus dispositivos Apple e aguarde um minuto com esta janela aberta. Pedir códigos repetidamente pode bloquear o início de sessão durante algum tempo.",
        "Pas de code ? Déverrouillez l’un de vos appareils Apple et patientez une minute avec cette fenêtre ouverte. Demander des codes à répétition peut bloquer la connexion un moment.",
        "Kein Code? Entsperre eines deiner Apple-Geräte und warte eine Minute bei geöffnetem Fenster. Wiederholtes Anfordern kann die Anmeldung eine Weile sperren.",
        "Nessun codice? Sblocca uno dei tuoi dispositivi Apple e attendi un minuto con questa finestra aperta. Richiedere codici di continuo può bloccare l’accesso per un po’."),
    "Each wrong passcode uses one of about ten recovery attempts. After the last one Apple permanently erases this recovery record. One correct entry is safe.": (
        "Cada código incorrecto gasta uno de unos diez intentos de recuperación. Tras el último, Apple borra para siempre este registro de recuperación. Una entrada correcta es segura.",
        "Cada código errado gasta uma de cerca de dez tentativas de recuperação. Após a última, a Apple apaga permanentemente este registo de recuperação. Uma entrada correta é segura.",
        "Chaque code erroné consomme l’une des dix tentatives de récupération environ. Après la dernière, Apple efface définitivement cet enregistrement de récupération. Une saisie correcte est sans risque.",
        "Jeder falsche Code verbraucht einen von etwa zehn Wiederherstellungsversuchen. Nach dem letzten löscht Apple diesen Wiederherstellungseintrag endgültig. Eine richtige Eingabe ist sicher.",
        "Ogni codice errato consuma uno dei circa dieci tentativi di recupero. Dopo l’ultimo, Apple cancella definitivamente questo record di recupero. Un inserimento corretto è sicuro."),
    "Apple Account email or phone": ("Correo o teléfono de la cuenta de Apple", "E-mail ou telefone da Conta Apple", "E-mail ou téléphone du compte Apple", "E-Mail oder Telefonnummer des Apple Accounts", "E-mail o telefono dell’Account Apple"),
    "Device passcode": ("Código de desbloqueo", "Código do dispositivo", "Code de l’appareil", "Gerätecode", "Codice del dispositivo"),
    "Join Keychain": ("Unirse al llavero", "Aderir ao Porta-chaves", "Rejoindre le trousseau", "Schlüsselbund beitreten", "Unisciti al portachiavi"),
    "Continue": ("Continuar", "Continuar", "Continuer", "Fortfahren", "Continua"),
    "Not Now": ("Ahora no", "Agora não", "Plus tard", "Nicht jetzt", "Non ora"),
    "I Know the Passcode": ("Sé el código", "Sei o código", "Je connais le code", "Ich kenne den Code", "Conosco il codice"),
    "Sync Now": ("Sincronizar ahora", "Sincronizar agora", "Synchroniser maintenant", "Jetzt synchronisieren", "Sincronizza ora"),
    "Show Passwords": ("Ver contraseñas", "Mostrar senhas", "Afficher les mots de passe", "Passwörter anzeigen", "Mostra password"),
    "Cancel Sign-In": ("Cancelar inicio de sesión", "Cancelar início de sessão", "Annuler la connexion", "Anmeldung abbrechen", "Annulla accesso"),
    # ---- controller messages
    "Copied — clears in 30 seconds": ("Copiado: se borra en 30 segundos", "Copiado: apaga-se em 30 segundos", "Copié — effacé dans 30 secondes", "Kopiert – wird in 30 Sekunden gelöscht", "Copiato: verrà cancellato tra 30 secondi"),
    "Keychain up to date — {n} passwords": ("Llavero al día: {n} contraseñas", "Porta-chaves atualizado: {n} senhas", "Trousseau à jour — {n} mots de passe", "Schlüsselbund aktuell – {n} Passwörter", "Portachiavi aggiornato: {n} password"),
    "{n} passwords": ("{n} contraseñas", "{n} senhas", "{n} mots de passe", "{n} Passwörter", "{n} password"),
    "Not connected": ("Sin conexión", "Sem ligação", "Non connecté", "Nicht verbunden", "Non connesso"),
    "Signing in…": ("Iniciando sesión…", "A iniciar sessão…", "Connexion…", "Anmeldung …", "Accesso in corso…"),
    "Syncing…": ("Sincronizando…", "A sincronizar…", "Synchronisation…", "Synchronisiert …", "Sincronizzazione…"),
    "Stopped": ("Detenido", "Parado", "Arrêté", "Angehalten", "Interrotto"),
    "Enter your Apple Account email and password.": ("Ingresa el correo y la contraseña de tu cuenta de Apple.", "Introduza o e-mail e a senha da sua Conta Apple.", "Saisissez l’e-mail et le mot de passe de votre compte Apple.", "Gib E-Mail-Adresse und Passwort deines Apple Accounts ein.", "Inserisci e-mail e password del tuo Account Apple."),
    "Enter the six digits shown on your device.": ("Ingresa los seis dígitos que aparecen en tu dispositivo.", "Introduza os seis dígitos mostrados no seu dispositivo.", "Saisissez les six chiffres affichés sur votre appareil.", "Gib die sechs Ziffern ein, die auf deinem Gerät angezeigt werden.", "Inserisci le sei cifre mostrate sul dispositivo."),
    "Choose one of the devices.": ("Elige uno de los dispositivos.", "Escolha um dos dispositivos.", "Choisissez l’un des appareils.", "Wähle eines der Geräte.", "Scegli uno dei dispositivi."),
    "This field cannot be empty.": ("Este campo no puede quedar vacío.", "Este campo não pode ficar vazio.", "Ce champ ne peut pas être vide.", "Dieses Feld darf nicht leer sein.", "Questo campo non può essere vuoto."),
    "That file can't be used as an icon: {error}": ("Ese archivo no sirve como ícono: {error}", "Esse ficheiro não pode ser usado como ícone: {error}", "Ce fichier ne peut pas servir d’icône : {error}", "Diese Datei kann nicht als Symbol verwendet werden: {error}", "Questo file non può essere usato come icona: {error}"),
    "Apple is limiting sign-in attempts from this computer. Wait at least an hour before trying again; retrying sooner extends the block.": (
        "Apple está limitando los intentos de inicio de sesión desde esta computadora. Espera al menos una hora antes de reintentar; reintentar antes alarga el bloqueo.",
        "A Apple está a limitar as tentativas de início de sessão deste computador. Aguarde pelo menos uma hora; tentar antes prolonga o bloqueio.",
        "Apple limite les tentatives de connexion depuis cet ordinateur. Attendez au moins une heure ; réessayer plus tôt prolonge le blocage.",
        "Apple begrenzt Anmeldeversuche von diesem Computer. Warte mindestens eine Stunde; frühere Versuche verlängern die Sperre.",
        "Apple sta limitando i tentativi di accesso da questo computer. Attendi almeno un’ora; riprovare prima prolunga il blocco."),
    "Apple's sign-in service refused this device identity (HTTP 503). Check that the anisette service is the Windows iCloud one and is running.": (
        "El servicio de inicio de sesión de Apple rechazó la identidad de este dispositivo (HTTP 503). Comprueba que el servicio de anisette sea el de iCloud para Windows y esté funcionando.",
        "O serviço de início de sessão da Apple recusou a identidade deste dispositivo (HTTP 503). Confirme que o serviço anisette é o do iCloud para Windows e está a funcionar.",
        "Le service de connexion d’Apple a refusé l’identité de cet appareil (HTTP 503). Vérifiez que le service anisette est celui d’iCloud pour Windows et qu’il fonctionne.",
        "Apples Anmeldedienst hat die Identität dieses Geräts abgelehnt (HTTP 503). Prüfe, ob der Anisette-Dienst der von iCloud für Windows ist und läuft.",
        "Il servizio di accesso Apple ha rifiutato l’identità di questo dispositivo (HTTP 503). Verifica che il servizio anisette sia quello di iCloud per Windows e sia attivo."),
    "Apple says the Apple Account email or password is incorrect.": ("Apple dice que el correo o la contraseña de la cuenta de Apple son incorrectos.", "A Apple indica que o e-mail ou a senha da Conta Apple estão incorretos.", "Apple indique que l’e-mail ou le mot de passe du compte Apple est incorrect.", "Laut Apple sind E-Mail-Adresse oder Passwort des Apple Accounts falsch.", "Apple indica che l’e-mail o la password dell’Account Apple non sono corrette."),
    "Apple rejected the sign-in request (-22410). This usually means the anisette identity does not match; restart the anisette service and try again later.": (
        "Apple rechazó la solicitud de inicio de sesión (-22410). Suele significar que la identidad de anisette no coincide; reinicia el servicio de anisette y vuelve a intentarlo más tarde.",
        "A Apple rejeitou o pedido de início de sessão (-22410). Normalmente significa que a identidade anisette não corresponde; reinicie o serviço anisette e tente mais tarde.",
        "Apple a refusé la demande de connexion (-22410). Cela signifie souvent que l’identité anisette ne correspond pas ; redémarrez le service anisette et réessayez plus tard.",
        "Apple hat die Anmeldung abgelehnt (-22410). Meist passt die Anisette-Identität nicht; starte den Anisette-Dienst neu und versuche es später erneut.",
        "Apple ha rifiutato la richiesta di accesso (-22410). Di solito l’identità anisette non corrisponde; riavvia il servizio anisette e riprova più tardi."),
    "The anisette service at {url} isn't answering. Start it, then try again.": ("El servicio de anisette en {url} no responde. Inícialo y vuelve a intentarlo.", "O serviço anisette em {url} não responde. Inicie-o e tente de novo.", "Le service anisette à {url} ne répond pas. Démarrez-le puis réessayez.", "Der Anisette-Dienst unter {url} antwortet nicht. Starte ihn und versuche es erneut.", "Il servizio anisette su {url} non risponde. Avvialo e riprova."),
    "The device passcode was not accepted. Each wrong passcode uses one of about ten recovery attempts; check the device before trying again.": (
        "El código de desbloqueo no fue aceptado. Cada código incorrecto gasta uno de unos diez intentos; verifica el dispositivo antes de volver a intentar.",
        "O código do dispositivo não foi aceite. Cada código errado gasta uma de cerca de dez tentativas; confirme o dispositivo antes de tentar de novo.",
        "Le code de l’appareil n’a pas été accepté. Chaque code erroné consomme l’une des dix tentatives environ ; vérifiez l’appareil avant de réessayer.",
        "Der Gerätecode wurde nicht akzeptiert. Jeder falsche Code verbraucht einen von etwa zehn Versuchen; prüfe das Gerät, bevor du es erneut versuchst.",
        "Il codice del dispositivo non è stato accettato. Ogni codice errato consuma uno dei circa dieci tentativi; controlla il dispositivo prima di riprovare."),
    "Cancelled. Nothing was changed.": ("Cancelado. No se cambió nada.", "Cancelado. Nada foi alterado.", "Annulé. Rien n’a été modifié.", "Abgebrochen. Nichts wurde geändert.", "Annullato. Non è stato modificato nulla."),
}

_ORDER = ("es", "pt", "fr", "de", "it")


def translate(text: str, language: str) -> str:
    if language == "en" or language not in _ORDER:
        return text
    row = _T.get(text)
    return row[_ORDER.index(language)] if row else text


def system_language() -> str:
    """The desktop's language when the app has it, English otherwise."""
    try:
        from PyQt6.QtCore import QLocale
        for name in QLocale.system().uiLanguages() or [QLocale.system().name()]:
            code = name.replace("_", "-").split("-")[0].lower()
            if code in LANGUAGES:
                return code
    except Exception:  # noqa: BLE001 - no Qt locale means English
        pass
    return "en"


def resolve(preference: str) -> str:
    return preference if preference in LANGUAGES else system_language()
