"""Interface translations. English strings are the keys; a missing entry falls back to
English. `{name}` placeholders are filled by the caller after translation."""

from __future__ import annotations

import re

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
    "Passcode": ("Código de desbloqueo", "Código de desbloqueio", "Code d’accès", "Gerätecode", "Codice di sblocco"),
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

# ---- engine messages (icp prints these in English; the window shows them translated)
_T.update({
    "Already joined; syncing…": ("Ya estás unido; sincronizando…", "Já aderiu; a sincronizar…", "Déjà membre ; synchronisation…", "Bereits beigetreten; wird synchronisiert …", "Già unito; sincronizzazione…"),
    "Looking for your devices' recovery records…": ("Buscando los registros de recuperación de tus dispositivos…", "A procurar os registos de recuperação dos seus dispositivos…", "Recherche des enregistrements de récupération de vos appareils…", "Wiederherstellungseinträge deiner Geräte werden gesucht …", "Ricerca dei record di recupero dei tuoi dispositivi…"),
    "Several devices can let this computer in. Pick one.": ("Varios dispositivos pueden dar acceso a esta computadora. Elige uno.", "Vários dispositivos podem dar acesso a este computador. Escolha um.", "Plusieurs appareils peuvent autoriser cet ordinateur. Choisissez-en un.", "Mehrere Geräte können diesen Computer zulassen. Wähle eines.", "Più dispositivi possono autorizzare questo computer. Scegline uno."),
    "Using {device}, the only device available.": ("Se usará {device}, el único dispositivo disponible.", "Será usado {device}, o único dispositivo disponível.", "Utilisation de {device}, le seul appareil disponible.", "{device} wird verwendet, das einzige verfügbare Gerät.", "Verrà usato {device}, l’unico dispositivo disponibile."),
    "You'll need the passcode of {device}.": ("Vas a necesitar el código de desbloqueo de {device}.", "Vai precisar do código de desbloqueio de {device}.", "Il vous faudra le code de déverrouillage de {device}.", "Du brauchst den Code zum Entsperren von {device}.", "Ti servirà il codice di sblocco di {device}."),
    "This step can't be undone: each wrong passcode uses one of about ten attempts.": ("Este paso no se puede deshacer: cada código incorrecto gasta uno de unos diez intentos.", "Este passo não pode ser desfeito: cada código errado gasta uma de cerca de dez tentativas.", "Cette étape est irréversible : chaque code erroné consomme l’une des dix tentatives environ.", "Dieser Schritt ist endgültig: Jeder falsche Code verbraucht einen von etwa zehn Versuchen.", "Questo passaggio è irreversibile: ogni codice errato consuma uno dei circa dieci tentativi."),
    "Stopped before using any recovery attempt. You're signed in but haven't joined the keychain yet.": ("Se detuvo sin gastar ningún intento de recuperación. Tienes la sesión iniciada, pero todavía no te uniste al llavero.", "Parou sem gastar nenhuma tentativa de recuperação. Tem a sessão iniciada, mas ainda não aderiu ao Porta-chaves.", "Arrêté sans consommer de tentative de récupération. Vous êtes connecté mais n’avez pas encore rejoint le trousseau.", "Ohne Wiederherstellungsversuch angehalten. Du bist angemeldet, aber noch nicht dem Schlüsselbund beigetreten.", "Interrotto senza usare tentativi di recupero. Hai eseguito l’accesso ma non ti sei ancora unito al portachiavi."),
    "Joined the keychain. Decrypted {n} passwords.": ("Te uniste al llavero. Se descifraron {n} contraseñas.", "Aderiu ao Porta-chaves. Foram desencriptadas {n} senhas.", "Trousseau rejoint. {n} mots de passe déchiffrés.", "Dem Schlüsselbund beigetreten. {n} Passwörter entschlüsselt.", "Unito al portachiavi. {n} password decifrate."),
    "Decrypted {n} passwords.": ("Se descifraron {n} contraseñas.", "Foram desencriptadas {n} senhas.", "{n} mots de passe déchiffrés.", "{n} Passwörter entschlüsselt.", "{n} password decifrate."),
    "Signed in as {user}.": ("Sesión iniciada como {user}.", "Sessão iniciada como {user}.", "Connecté en tant que {user}.", "Angemeldet als {user}.", "Accesso eseguito come {user}."),
    "Apple sent a verification code.": ("Apple envió un código de verificación.", "A Apple enviou um código de verificação.", "Apple a envoyé un code de validation.", "Apple hat einen Bestätigungscode gesendet.", "Apple ha inviato un codice di verifica."),
    "Hide My Email needs its own verification code.": ("Ocultar mi correo necesita su propio código de verificación.", "Ocultar o meu e-mail precisa do seu próprio código de verificação.", "Masquer mon adresse e-mail demande son propre code de validation.", "„E-Mail-Adresse verbergen“ benötigt einen eigenen Bestätigungscode.", "Nascondi la mia email richiede un proprio codice di verifica."),
    "Saved {n} Hide My Email addresses.": ("Se guardaron {n} direcciones de Ocultar mi correo.", "Foram guardados {n} endereços de Ocultar o meu e-mail.", "{n} adresses Masquer mon adresse e-mail enregistrées.", "{n} Adressen von „E-Mail-Adresse verbergen“ gespeichert.", "Salvati {n} indirizzi di Nascondi la mia email."),
    "Session expired; signing in again with the saved password…": ("La sesión expiró; iniciando sesión otra vez con la contraseña guardada…", "A sessão expirou; a iniciar sessão novamente com a senha guardada…", "Session expirée ; reconnexion avec le mot de passe enregistré…", "Sitzung abgelaufen; erneute Anmeldung mit dem gespeicherten Passwort …", "Sessione scaduta; nuovo accesso con la password salvata…"),
    "Sign-in failed: {detail}": ("Falló el inicio de sesión: {detail}", "O início de sessão falhou: {detail}", "Échec de la connexion : {detail}", "Anmeldung fehlgeschlagen: {detail}", "Accesso non riuscito: {detail}"),
    "Joining the keychain failed: {detail}": ("No se pudo unir al llavero: {detail}", "Não foi possível aderir ao Porta-chaves: {detail}", "Impossible de rejoindre le trousseau : {detail}", "Beitritt zum Schlüsselbund fehlgeschlagen: {detail}", "Impossibile unirsi al portachiavi: {detail}"),
    "Joined, but the sync failed: {detail}": ("Te uniste, pero falló la sincronización: {detail}", "Aderiu, mas a sincronização falhou: {detail}", "Trousseau rejoint, mais la synchronisation a échoué : {detail}", "Beigetreten, aber die Synchronisierung ist fehlgeschlagen: {detail}", "Unito, ma la sincronizzazione non è riuscita: {detail}"),
    "Sync failed: {detail}": ("Falló la sincronización: {detail}", "A sincronização falhou: {detail}", "Échec de la synchronisation : {detail}", "Synchronisierung fehlgeschlagen: {detail}", "Sincronizzazione non riuscita: {detail}"),
    "No device can let this computer join through this path.": ("Ningún dispositivo puede dar acceso a esta computadora por esta vía.", "Nenhum dispositivo pode dar acesso a este computador por esta via.", "Aucun appareil ne peut autoriser cet ordinateur par cette voie.", "Kein Gerät kann diesen Computer auf diesem Weg zulassen.", "Nessun dispositivo può autorizzare questo computer in questo modo."),
    "iCloud didn't provide the keychain address, so the keychain can't be joined.": ("iCloud no dio la dirección del llavero, así que no se puede unir.", "O iCloud não forneceu o endereço do Porta-chaves, por isso não é possível aderir.", "iCloud n’a pas fourni l’adresse du trousseau ; impossible de le rejoindre.", "iCloud hat die Schlüsselbund-Adresse nicht geliefert, daher ist kein Beitritt möglich.", "iCloud non ha fornito l’indirizzo del portachiavi, quindi non è possibile unirsi."),
    "Apple accepted the account and code, but iCloud didn't provide its service tokens, so the keychain can't be joined.": ("Apple aceptó la cuenta y el código, pero iCloud no entregó sus tokens de servicio, así que no se puede unir al llavero.", "A Apple aceitou a conta e o código, mas o iCloud não forneceu os tokens de serviço, por isso não é possível aderir ao Porta-chaves.", "Apple a accepté le compte et le code, mais iCloud n’a pas fourni ses jetons de service ; impossible de rejoindre le trousseau.", "Apple hat Account und Code akzeptiert, aber iCloud hat keine Diensttokens geliefert, daher ist kein Beitritt möglich.", "Apple ha accettato account e codice, ma iCloud non ha fornito i token di servizio, quindi non è possibile unirsi al portachiavi."),
    "Another operation is already running.": ("Ya hay otra operación en curso.", "Já está a decorrer outra operação.", "Une autre opération est déjà en cours.", "Ein anderer Vorgang läuft bereits.", "È già in corso un’altra operazione."),
    "Another sync is already running.": ("Ya hay otra sincronización en curso.", "Já está a decorrer outra sincronização.", "Une autre synchronisation est déjà en cours.", "Eine andere Synchronisierung läuft bereits.", "È già in corso un’altra sincronizzazione."),
    "Sync skipped: {detail}": ("Sincronización omitida: {detail}", "Sincronização ignorada: {detail}", "Synchronisation ignorée : {detail}", "Synchronisierung übersprungen: {detail}", "Sincronizzazione saltata: {detail}"),
    "You're not signed in. Open Apple Account to sign in.": ("No tienes la sesión iniciada. Abre Cuenta de Apple para iniciar sesión.", "Não tem sessão iniciada. Abra Conta Apple para iniciar sessão.", "Vous n’êtes pas connecté. Ouvrez Compte Apple pour vous connecter.", "Du bist nicht angemeldet. Öffne „Apple Account“, um dich anzumelden.", "Non hai eseguito l’accesso. Apri Account Apple per accedere."),
    "This computer hasn't joined the keychain yet. Open Apple Account to finish.": ("Esta computadora todavía no se unió al llavero. Abre Cuenta de Apple para terminar.", "Este computador ainda não aderiu ao Porta-chaves. Abra Conta Apple para concluir.", "Cet ordinateur n’a pas encore rejoint le trousseau. Ouvrez Compte Apple pour terminer.", "Dieser Computer ist dem Schlüsselbund noch nicht beigetreten. Öffne „Apple Account“, um abzuschließen.", "Questo computer non si è ancora unito al portachiavi. Apri Account Apple per completare."),
    "The passcode was empty, so no attempt was used.": ("El código estaba vacío, así que no se gastó ningún intento.", "O código estava vazio, por isso nenhuma tentativa foi gasta.", "Le code était vide ; aucune tentative n’a été consommée.", "Der Code war leer, daher wurde kein Versuch verbraucht.", "Il codice era vuoto, quindi non è stato usato alcun tentativo."),
    "Couldn't refresh the iCloud session: {detail}": ("No se pudo renovar la sesión de iCloud: {detail}", "Não foi possível renovar a sessão do iCloud: {detail}", "Impossible de renouveler la session iCloud : {detail}", "Die iCloud-Sitzung konnte nicht erneuert werden: {detail}", "Impossibile rinnovare la sessione iCloud: {detail}"),
    "Hide My Email is unavailable: {detail}": ("Ocultar mi correo no está disponible: {detail}", "Ocultar o meu e-mail não está disponível: {detail}", "Masquer mon adresse e-mail est indisponible : {detail}", "„E-Mail-Adresse verbergen“ ist nicht verfügbar: {detail}", "Nascondi la mia email non è disponibile: {detail}"),
    "Couldn't fetch the iCloud service addresses: {detail}": ("No se pudieron obtener las direcciones de servicio de iCloud: {detail}", "Não foi possível obter os endereços de serviço do iCloud: {detail}", "Impossible d’obtenir les adresses de service iCloud : {detail}", "Die iCloud-Dienstadressen konnten nicht abgerufen werden: {detail}", "Impossibile ottenere gli indirizzi di servizio iCloud: {detail}"),
    "Couldn't open the vault: {detail}": ("No se pudo abrir la bóveda: {detail}", "Não foi possível abrir o cofre: {detail}", "Impossible d’ouvrir le coffre : {detail}", "Der Tresor konnte nicht geöffnet werden: {detail}", "Impossibile aprire la cassaforte: {detail}"),
})

_ENGINE = [
    (r"Already joined; syncing\.*", "Already joined; syncing…"),
    (r"Discovering escrow bottles\.*", "Looking for your devices' recovery records…"),
    (r"Multiple escrow bottles found.*", "Several devices can let this computer in. Pick one."),
    (r"Using the only escrow bottle: (?P<device>.+)", "Using {device}, the only device available."),
    (r"Joining iCloud Keychain will use the passcode of: (?P<device>.+)", "You'll need the passcode of {device}."),
    (r"This is IRREVERSIBLE.*", "This step can't be undone: each wrong passcode uses one of about ten attempts."),
    (r"Aborted.*no escrow attempt spent.*", "Stopped before using any recovery attempt. You're signed in but haven't joined the keychain yet."),
    (r"Joined the keychain\. Synced (?P<n>\d+) credential\(s\)\.", "Joined the keychain. Decrypted {n} passwords."),
    (r"Synced (?P<n>\d+) credential\(s\) into the vault\.", "Decrypted {n} passwords."),
    (r"Signed in as (?P<user>.+)\.", "Signed in as {user}."),
    (r"A 2FA code was sent to your trusted Apple devices for Hide My Email\.", "Hide My Email needs its own verification code."),
    (r"Hide My Email requires a separate.*", "Hide My Email needs its own verification code."),
    (r"A 2FA code was sent to .+\.", "Apple sent a verification code."),
    (r"Cached (?P<n>\d+) Hide My Email alias\(es\)\.", "Saved {n} Hide My Email addresses."),
    (r"iCloud token expired.*", "Session expired; signing in again with the saved password…"),
    (r"sign-in failed: (?P<detail>.+)", "Sign-in failed: {detail}"),
    (r"join failed: (?P<detail>.+)", "Joining the keychain failed: {detail}"),
    (r"joined, but sync failed: (?P<detail>.+)", "Joined, but the sync failed: {detail}"),
    (r"sync failed: (?P<detail>.+)", "Sync failed: {detail}"),
    (r"no recoverable escrow bottle.*", "No device can let this computer join through this path."),
    (r"no escrow URL cached.*", "iCloud didn't provide the keychain address, so the keychain can't be joined."),
    (r"Apple ID and 2FA were accepted.*", "Apple accepted the account and code, but iCloud didn't provide its service tokens, so the keychain can't be joined."),
    (r"busy - another sync is already running", "Another sync is already running."),
    (r"skipped: (?P<detail>.+)", "Sync skipped: {detail}"),
    (r"not signed in - run: icp login", "You're not signed in. Open Apple Account to sign in."),
    (r"not joined to the keychain - run: icp login", "This computer hasn't joined the keychain yet. Open Apple Account to finish."),
    (r"empty passcode.*", "The passcode was empty, so no attempt was used."),
    (r"(?:could not refresh the iCloud token|iCloud login needed): (?P<detail>.+)", "Couldn't refresh the iCloud session: {detail}"),
    (r"Warning: Hide My Email unavailable: (?P<detail>.+)", "Hide My Email is unavailable: {detail}"),
    (r"Warning: could not fetch iCloud service URLs: (?P<detail>.+)", "Couldn't fetch the iCloud service addresses: {detail}"),
    (r"could not open the vault: (?P<detail>.+)", "Couldn't open the vault: {detail}"),
]
_ENGINE = [(re.compile(pattern, re.DOTALL), template) for pattern, template in _ENGINE]


def translate_engine(text: str, language: str) -> str:
    """The window's wording for a message the icp engine printed; unknown text is unchanged."""
    stripped = (text or "").strip()
    for pattern, template in _ENGINE:
        match = pattern.fullmatch(stripped)
        if match:
            return translate(template, language).format(**match.groupdict())
    return text

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
