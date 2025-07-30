from database_connector import DatabaseInterface
import ast
import pandas as pd
from scipy.stats import f_oneway
from collections import defaultdict
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from sklearn.manifold import TSNE
import hdbscan
import numpy as np


def anova(db_connection: DatabaseInterface, table_name, min_sample_size=0):
	'''
		this function runs the annova on the dataset and render the associated F_score and p_value
		Args:
			table_name (str): the name of the table on which you want to run the ANOVA
			min_sample_size (int): default = 0, is used to exclude categories that does not have enough measurement.
		the selected table MUST have the following signature:

		groups | measurement

		exemple with the product_type_age table:

		type | age
		----------
		'Coat', '36'
		'Coat', '36'
		'Hat/beanie', '32'
		...

		min_sample_size is used to exclude categories that does not have enough measurement.
		default = 0: all categories are selected

		return type is: dict
		{
			"F-statistic": round(f_stat, 3),
			"p-value": round(p_value, 3)
		}
	'''
	try: 
		query = f"SELECT * FROM {table_name};"

		result = db_connection.read_only_query(query)
		categories = defaultdict(list)

		for product_type, age in result:
			if age is not None:
				if not isinstance(age, int):
					age = int(age)
				categories[product_type].append(age)

		categories_filtered = {
			k: v for k, v in categories.items() if len(v) > min_sample_size
		}

		categories_filtered = list(categories_filtered.values())
		f_stat, p_value = f_oneway(*categories_filtered)
	except Exception as e:
		return f"Annova function fail to run: {e}"
	return {
		"F-statistic": round(f_stat, 3),
		"p-value": round(p_value, 3)
	}

def tukey_test(db_connection: DatabaseInterface, table_name, min_sample_size=0):
	'''
		this function runs a Tukey's HSD (Honestly Significant Difference) test — a post-hoc analysis following ANOVA. 
		It tells you which specific pairs of groups differ significantly in their means
		IT is meant to be used after you run a successful anova and you obtain sgnificant F-satatistics and p-value
		table_name is the name of the table on which you want to run the ANOVA
		the selected table MUST have the following signature:

		groups | measurement

		exemple with the product_type_age table:

		type | age
		----------
		'Coat', 36
		'Coat', 36
		'Hat/beanie', 32
		...

		min_sample_size is used to exclude categories that does not have enough measurement.
		default = 0: all categories are selected

		the return result is the raw dataframe that correspond to the pair wize categorie that reject the hypothesis of non statistically difference between two group
		the signature of the dataframe is the following:
		group1 | group2 | meandiff p-adj | lower | upper | reject (only true)
	
	'''
	try:
		query = f"SELECT * FROM {table_name};"

		result = db_connection.read_only_query(query)
		categories = defaultdict(list)

		for product_type, age in result:
			if age is not None:
				if not isinstance(age, int):
					age = int(age)
				categories[product_type].append(age)

		categories_filtered = {
			k: v for k, v in categories.items() if len(v) > min_sample_size
		}

		flat_df = pd.DataFrame([
			{'product_type_name': k, 'age': age}
			for k, ages in categories_filtered.items()
			for age in ages
		])

		# Tukey HSD
		tukey = pairwise_tukeyhsd(endog=flat_df['age'],
								groups=flat_df['product_type_name'],
								alpha=0.05)
		tukey_df = pd.DataFrame(data=tukey.summary().data[1:], columns=tukey.summary().data[0])

		significant_results = tukey_df[tukey_df['reject'] == True]
	except Exception as e:
		return f"Tukey test function fail to run: {e}"
	return significant_results

def embedding_clustering(db_connection: DatabaseInterface, query):
	"""
		this tool allow to run a TSNE dimensionality reduction algorythme and a clustering (HDBSCAN) on top of that.

		the input query, is a sql query that MUST return a table with at least the item id and the corresponding embeddding.

		exemple:
		result = db_connection.read_only_query(query)
		result shape:
		article_id | embedding
		0125456    | [0.3, 0.5 ...]

		the return is a dictionnary that has the following format:

			return {
				"ids": ids,
				"x_axis": tsne_projection_x_list,
				"y_axis": tsne_projection_y_list,
				"labels": labels
			}
	"""
	try:
		result = db_connection.read_only_query(query)
		tsne = TSNE(n_components=2, random_state=42)

		ids = [item[0] for item in result]
		article_embeddings = [ast.literal_eval(item[1]) for item in result]
		tsne_proj = tsne.fit_transform(np.array(article_embeddings))


		clusterer = hdbscan.HDBSCAN(min_cluster_size=10)
		labels = clusterer.fit_predict(tsne_proj)
	except Exception as e:
		return f"Embedding clustering function fail to run: {e}"
	return {
		"ids": ids,
		"x_axis": tsne_proj[:, 0],
		"y_axis": tsne_proj[:, 1],
		"labels": labels
	}

def vector_centroid(db_connection: DatabaseInterface, query):
	try:
		result = db_connection.read_only_query(query)
		embeddings = np.array([ast.literal_eval(item[0]) for item in result])
		if embeddings.ndim != 2:
			raise ValueError("Input must be a 2D array of shape (n_vectors, vector_dimension)")
	except Exception as e:
		return f"Vector centroid function fail to run: {e}"
	return np.mean(embeddings, axis=0)




