# DISTRIBUCIÓN
        pedido_sorted = sorted(pedido_items, key=lambda x: PRODUCTOS_BASE[x['ref']]['largo_ft'], reverse=True)
        mapa_vertical = []
        saldos = []
        
        MAX_SALDO = 60  # Límite solicitado para los bloques amarillos

        for item in pedido_sorted:
            paq_tam = PRODUCTOS_BASE[item['ref']]['paquete']
            completos = item["cant"] // paq_tam
            sobra_total = item["cant"] % paq_tam
            
            # 1. Agregar paquetes completos (Verdes)
            for _ in range(completos):
                mapa_vertical.append({"label": item["tipo"], "cant": paq_tam})
            
            # 2. Fragmentar el saldo en bloques de máximo 60 (Amarillos)
            while sobra_total > 0:
                if sobra_total > MAX_SALDO:
                    saldos.append({"label": item["tipo"], "cant": MAX_SALDO})
                    sobra_total -= MAX_SALDO
                else:
                    saldos.append({"label": item["tipo"], "cant": sobra_total})
                    sobra_total = 0

        # --- El resto del código de renderizado (MAPA VISUAL) se mantiene igual ---
