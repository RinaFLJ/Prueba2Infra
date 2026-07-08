import hashlib

def calculate_merkle_root(leaves):
    """Calcula de forma simplificada la raiz de Merkle de una lista de eventos."""
    if not leaves:
        return hashlib.sha256(b"").hexdigest()
    
    # Asegurar que todos los elementos sean hashes tipificados en string
    current_level = [hashlib.sha256(str(leaf).encode('utf-8')).hexdigest() for leaf in leaves]
    
    while len(current_level) > 1:
        next_level = []
        # Agrupar de a pares
        for i in range(0, len(current_level), 2):
            left = current_level[i]
            # Si es impar, el elemento se duplica para formar el par
            right = current_level[i+1] if i+1 < len(current_level) else current_level[i]
            combined = left + right
            next_level.append(hashlib.sha256(combined.encode('utf-8')).hexdigest())
        current_level = next_level
        
    return current_level[0]