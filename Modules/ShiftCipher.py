class ShiftCipher:
    ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+[]{}|;:'\",.<>?/`~"

    def shift_text(self, text, direction):
        """Effectue un décalage circulaire normal à gauche ou à droite."""
        if len(set(text)) == 1:  # Vérifier si tous les caractères sont identiques
            return self.shift_same_chars(text, direction)

        if direction == 'd':  # Décalage à droite
            return text[-1] + text[:-1]
        elif direction == 'g':  # Décalage à gauche
            return text[1:] + text[0]
        return None

    def shift_same_chars(self, text, direction):
        """Décale les caractères identiques selon l'alphabet défini."""
        shifted_text = ""
        for char in text:
            if char in self.ALPHABET:
                index = self.ALPHABET.index(char)
                if direction == 'd':  # Décalage à droite dans l'alphabet
                    new_index = (index + 1) % len(self.ALPHABET)
                else:  # Décalage à gauche dans l'alphabet
                    new_index = (index - 1) % len(self.ALPHABET)
                shifted_text += self.ALPHABET[new_index]
            else:
                shifted_text += char  # Conserver les caractères non reconnus intacts
        return shifted_text

    def encrypt(self, text):
        """Crypte un texte en appliquant un décalage et en ajoutant un indicateur."""
        if not text.strip():
            print("Erreur : Le message ne peut pas être vide ou composé uniquement d'espaces.")
            return None
        
        text = text.strip()
        if text[-1] in ('g', 'd'):
            text_to_shift, direction = text[:-1], text[-1]
        else:
            print("Erreur : Le message doit se terminer par 'g' (gauche) ou 'd' (droite).")
            return None
        
        if not text_to_shift:
            print("Erreur : Aucun texte à chiffrer trouvé avant l'indicateur.")
            return None

        encrypted_text = self.shift_text(text_to_shift, direction)
        return encrypted_text + direction  

    def decrypt(self, text):
        """Décrypte un texte en inversant le décalage selon l’indicateur."""
        if not text.strip():
            print("Erreur : Message vide.")
            return None

        text = text.strip()
        if text[-1] in ('g', 'd'):
            encrypted_text, direction = text[:-1], text[-1]
        else:
            print("Erreur : Format de message crypté invalide.")
            return None

        if not encrypted_text:
            print("Erreur : Aucun texte à décrypter trouvé avant l'indicateur.")
            return None

        decrypted_text = self.shift_text(encrypted_text, 'd' if direction == 'g' else 'g')
        return decrypted_text


# Menu principal
if __name__ == "__main__":
    cipher = ShiftCipher()
    choice = input("Voulez-vous crypter ou décrypter un message ? (crypter/decrypter) : ").strip().lower()
    
    if choice == "crypter":
        message = input("Entrez un message à crypter (ajoutez 'g' ou 'd' à la fin) : ").strip()
        encrypted_message = cipher.encrypt(message)
        if encrypted_message:
            print("Message crypté :", encrypted_message)
    
    elif choice == "decrypter":
        encrypted_message = input("Entrez le message crypté : ").strip()
        decrypted_message = cipher.decrypt(encrypted_message)
        if decrypted_message:
            print("Message décrypté :", decrypted_message)
        else:
            print("Échec du déchiffrement.")
    else:
        print("Choix invalide, fin du programme.")