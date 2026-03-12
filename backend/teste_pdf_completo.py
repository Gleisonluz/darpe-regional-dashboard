"""
Script de teste - gera PDF completo com colaboradores e hinos
Execute: python teste_pdf_completo.py
"""
import asyncio
import httpx

BASE_URL = "http://localhost:8000/api"

COLABORADORES = [
    {"nome_completo": "José Aparecido da Silva",    "comum_congregacao": "Cgg Central Itajaí",       "whatsapp": "47991110001", "senha": "teste123", "cargo_funcao_ministerio": "Musico e Encarregado Regional"},
    {"nome_completo": "Paulo Roberto Mendes",        "comum_congregacao": "Cgg Bairro dos Lírios",    "whatsapp": "47991110002", "senha": "teste123", "cargo_funcao_ministerio": "Diacono"},
    {"nome_completo": "Carlos Eduardo Ferreira",     "comum_congregacao": "Cgg Vila Nova",            "whatsapp": "47991110003", "senha": "teste123", "cargo_funcao_ministerio": "Anciao"},
    {"nome_completo": "Antônio Luiz Pereira",        "comum_congregacao": "Cgg Ressacada",            "whatsapp": "47991110004", "senha": "teste123", "cargo_funcao_ministerio": "Musico e Encarregado Local"},
    {"nome_completo": "Marcos Vinicius Souza",       "comum_congregacao": "Cgg Fazenda",              "whatsapp": "47991110005", "senha": "teste123", "cargo_funcao_ministerio": "Musico e Instrutor"},
    {"nome_completo": "João Batista Oliveira",       "comum_congregacao": "Cgg Central Itajaí",       "whatsapp": "47991110006", "senha": "teste123", "cargo_funcao_ministerio": "Musico"},
    {"nome_completo": "Pedro Henrique Costa",        "comum_congregacao": "Cgg Limoeiro",             "whatsapp": "47991110007", "senha": "teste123", "cargo_funcao_ministerio": "Cooperador de Jovens e Menores"},
    {"nome_completo": "Lucas Gabriel Almeida",       "comum_congregacao": "Cgg Sertão do Trombudo",   "whatsapp": "47991110008", "senha": "teste123", "cargo_funcao_ministerio": "Cooperador do Oficio Ministerial"},
    {"nome_completo": "Fernando José Rodrigues",     "comum_congregacao": "Cgg Barra do Rio",         "whatsapp": "47991110009", "senha": "teste123", "cargo_funcao_ministerio": "Porteiro"},
    {"nome_completo": "Roberto Carlos Nascimento",   "comum_congregacao": "Cgg Murta",                "whatsapp": "47991110010", "senha": "teste123", "cargo_funcao_ministerio": "Administracao"},
    {"nome_completo": "Sílvio Antunes Barbosa",      "comum_congregacao": "Cgg Imaruí",               "whatsapp": "47991110011", "senha": "teste123", "cargo_funcao_ministerio": "Auxiliar de Jovens e Menores"},
    {"nome_completo": "Renato Augusto Lima",         "comum_congregacao": "Cgg Central Itajaí",       "whatsapp": "47991110012", "senha": "teste123", "cargo_funcao_ministerio": "Colaborador(a) do EBI"},
    {"nome_completo": "Edson Marques Teixeira",      "comum_congregacao": "Cgg Porto Belo",           "whatsapp": "47991110013", "senha": "teste123", "cargo_funcao_ministerio": "Atendente DARPE"},
    {"nome_completo": "Gilmar Pereira dos Santos",   "comum_congregacao": "Cgg Navegantes",           "whatsapp": "47991110014", "senha": "teste123", "cargo_funcao_ministerio": "Colaborador DARPE"},
    {"nome_completo": "Valmir Conceição Souza",      "comum_congregacao": "Cgg Penha",                "whatsapp": "47991110015", "senha": "teste123", "cargo_funcao_ministerio": "Musico"},
]

RELATORIO = {
    "cidade": "Itajaí",
    "location_id": "1",
    "nome_local": "Congregação Central Itajaí",
    "data_servico": "2026-03-11",
    "atendente": "Irmão Gleison Luz",
    "leitura_palavra": "Salmos 23:1-6",
    "hinos": [143, 256, 389, 412, 501],
    "hora_inicio": "19:00",
    "hora_fim": "21:00",
    "evangelizados_presentes": 23,
    "colaboradores_presentes": 15,
    "observacoes": "Reunião de evangelização com boa presença. Palavra ministrada com unção. Vários irmãos colaboraram no serviço."
}


async def main():
    async with httpx.AsyncClient(timeout=30) as client:

        # 1. Cadastrar colaboradores
        print("\n📋 Cadastrando colaboradores...")
        qr_tokens = []
        for c in COLABORADORES:
            try:
                r = await client.post(f"{BASE_URL}/colaboradores/cadastro", json=c)
                if r.status_code == 200:
                    qr = r.json()["qr_token"]
                    qr_tokens.append(qr)
                    print(f"  ✅ {c['nome_completo']} — {c['cargo_funcao_ministerio']}")
                elif r.status_code == 400 and "já cadastrado" in r.text:
                    # já existe, busca o qr_token via login
                    r2 = await client.post(f"{BASE_URL}/colaboradores/login", json={
                        "whatsapp": c["whatsapp"], "senha": c["senha"]
                    })
                    if r2.status_code == 200:
                        qr = r2.json()["qr_token"]
                        qr_tokens.append(qr)
                        print(f"  ♻️  {c['nome_completo']} — já cadastrado, reutilizando")
                else:
                    print(f"  ❌ {c['nome_completo']} — erro: {r.text}")
            except Exception as e:
                print(f"  ❌ {c['nome_completo']} — exceção: {e}")

        # 2. Criar relatório
        print("\n📄 Criando relatório...")
        r = await client.post(f"{BASE_URL}/mission-reports", json=RELATORIO)
        if r.status_code not in (200, 201):
            print(f"  ❌ Erro ao criar relatório: {r.text}")
            return
        relatorio = r.json()
        reuniao_id = relatorio.get("id") or relatorio.get("_id")
        print(f"  ✅ Relatório criado — ID: {reuniao_id}")

        # 3. Check-in dos colaboradores
        print("\n📲 Registrando presenças via QR code...")
        for i, qr in enumerate(qr_tokens):
            try:
                r = await client.post(f"{BASE_URL}/presencas-colaboradores/checkin", json={
                    "qr_token": qr,
                    "reuniao_id": reuniao_id
                })
                if r.status_code == 200:
                    nome = COLABORADORES[i]["nome_completo"]
                    print(f"  ✅ Check-in: {nome}")
                else:
                    print(f"  ❌ Erro check-in {i+1}: {r.text}")
            except Exception as e:
                print(f"  ❌ Exceção check-in {i+1}: {e}")

        # 4. Gerar PDF
        print("\n📥 Gerando PDF...")
        r = await client.get(f"{BASE_URL}/mission-reports/{reuniao_id}/pdf")
        if r.status_code == 200:
            nome_arquivo = f"teste_relatorio_{reuniao_id[:8]}.pdf"
            with open(nome_arquivo, "wb") as f:
                f.write(r.content)
            print(f"  ✅ PDF salvo como: {nome_arquivo}")
            print(f"\n🎉 Pronto! Abra o arquivo '{nome_arquivo}' para ver o resultado.")
        else:
            print(f"  ❌ Erro ao gerar PDF: {r.text}")


if __name__ == "__main__":
    asyncio.run(main())
