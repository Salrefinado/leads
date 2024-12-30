from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Dados iniciais
regions = {
    "SPO": ["Romerito Rocha Paz", "Thalita Lima Alves Cunha", "Luiz Fernando De Oliveira Santos"],
    "RJ": ["Renan Martins Pereira De Albuquerque", "Rodrigo Chamorro"],
    "MG": ["Valeria Mercedes Mario Oliveira", "Larissa Rayanne", "Joao Dario Da Silva"],
    "SPI": ["Ana Vytoria Batista Gomes", "Daniel Felipe Burbano", "Daniel Henrique Cristiani"],
    "RCE": ["Fabio Fernando Da Silva", "Mateus Costa Nogueira Da Silva"],
    "CTA": ["Gustavo Machado", "Nicolle Fernanda Moreno Baptista", "Marissa Silva de Andrade"],
    "POA": ["Mosara da Silva"]
}

# Inicializa os dados dos consultores
consultor_data = {
    consultor: {"leads_received": 0, "leads": []}
    for group in regions.values()
    for consultor in group
}

# Índices para rastrear o próximo consultor de cada região
region_indexes = {region: 0 for region in regions}


@app.route('/')
def index():
    return render_template('index.html', regions=regions, consultor_data=consultor_data)


@app.route('/get_leads', methods=['POST'])
def get_leads():
    consultor_name = request.form['consultor_name']
    if consultor_name in consultor_data:
        return jsonify(success=True, leads=consultor_data[consultor_name]["leads"])
    return jsonify(success=False, message="Consultor não encontrado.")


@app.route('/distribute_lead', methods=['POST'])
def distribute_lead():
    lead_id = request.form['lead_id']
    region = request.form['region']

    if region in regions and regions[region]:
        # Pega o índice atual para a região
        current_index = region_indexes[region]
        consultor = regions[region][current_index]

        # Atualiza o índice para o próximo consultor
        region_indexes[region] = (current_index + 1) % len(regions[region])

        # Atribui o lead ao consultor
        consultor_data[consultor]["leads_received"] += 1
        consultor_data[consultor]["leads"].append(lead_id)

        # Obter a quantidade de leads recebidos
        leads_received = consultor_data[consultor]["leads_received"]

        return jsonify(
            success=True,
            assigned_to=consultor,
            region=region,
            leads_received=leads_received,
            lead_id=lead_id
        )

    return jsonify(success=False, message="Nenhum consultor disponível na região.")


@app.route('/add_consultor', methods=['POST'])
def add_consultor():
    region = request.form['region']
    consultor_name = request.form['consultor_name']

    if region in regions:
        if consultor_name not in consultor_data:
            regions[region].append(consultor_name)
            consultor_data[consultor_name] = {"leads_received": 0, "leads": []}
            return jsonify(success=True)
        return jsonify(success=False, message="Consultor já existe.")
    return jsonify(success=False, message="Região inválida.")


@app.route('/edit_consultor', methods=['POST'])
def edit_consultor():
    old_name = request.form['old_name']
    new_name = request.form['new_name']

    if old_name in consultor_data:
        if new_name not in consultor_data:
            # Atualiza o nome do consultor
            consultor_data[new_name] = consultor_data.pop(old_name)

            # Atualiza nas regiões
            for region, consultors in regions.items():
                if old_name in consultors:
                    consultors[consultors.index(old_name)] = new_name
                    break
            return jsonify(success=True)
        return jsonify(success=False, message="O nome do consultor já existe.")
    return jsonify(success=False, message="Consultor não encontrado.")


@app.route('/delete_consultor', methods=['POST'])
def delete_consultor():
    consultor_name = request.form['consultor_name']

    if consultor_name in consultor_data:
        # Remove o consultor dos dados
        del consultor_data[consultor_name]

        # Remove o consultor da região
        for region, consultors in regions.items():
            if consultor_name in consultors:
                consultors.remove(consultor_name)
                break
        return jsonify(success=True)
    return jsonify(success=False, message="Consultor não encontrado.")


@app.route('/reset', methods=['POST'])
def reset_data():
    # Resetando as contagens de leads
    for consultor in consultor_data:
        consultor_data[consultor]["leads_received"] = 0
        consultor_data[consultor]["leads"] = []
    
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=True)
