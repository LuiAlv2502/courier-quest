import json

class Scoreboard:
	def __init__(self, json_path):
		self.json_path = json_path
		self.max_scores = 5
		self.scores = self.load_scores()
		self.sort_scores()

	def load_scores(self):
		# cargar los scores desde archivo JSON, si no existen, crea una lista vacía
		try:
			with open(self.json_path, 'r', encoding='utf-8') as f:
				data = json.load(f)
				return data.get('scores', [])[:self.max_scores]
		except Exception:
			return []

	def save_scores(self):
		#guardar los scores en el archivo JSON
		try:
			with open(self.json_path, 'w', encoding='utf-8') as f:
				json.dump({'scores': self.scores}, f, ensure_ascii=False, indent=4)
		except Exception as e:
			print(f"Error al guardar puntajes: {e}")

	def sort_scores(self):
		# algoritmo de ordenamiento por inserción
		scores = self.scores
		for i in range(1, len(scores)):
			key = scores[i]
			j = i - 1
			while j >= 0 and scores[j]['score'] < key['score']:
				scores[j + 1] = scores[j]
				j -= 1
			scores[j + 1] = key
		self.scores = scores[:self.max_scores]

	def add_score(self, score):
		self.scores.append({'score': score})
		self.sort_scores()
		self.scores = self.scores[:self.max_scores]
		self.save_scores()
		# devuelve el índice del nuevo entry si está en el top
		for idx, entry in enumerate(self.scores):
			if entry['score'] == score:
				return idx
		return None

	def get_scores(self):
		return self.scores

#lista de maximo 5 puntuaciones con ordenamiento de mayor a menos, valores enteros que son los scores
#crear archivo scores.json
"""
9. Condiciones de victoria/derrota y puntaje
§ Puntaje	final	(sugerido):
score_base =	suma	de	pagos	*	pay_mult	(por	reputación	alta)
bonus_tiempo	=	+X	si	terminas	antes	del	20%	del	tiempo	restante
penalizaciones	=	-Y	por	cancelaciones/caídas	(opcional)
score	=	score_base	+	bonus_tiempo	- penalizaciones
La	tabla	de	puntajes	se	almacenará	en	un	archivo	JSON	de manera	ordenada	(de	mayor	a	
menor).
manejar la lista donde se guardan las puntuaciones

Persistencia de archivos:
•	Guardado	binario:	/saves/slot1.sav
•	Puntajes:	/data/puntajes.json
"""