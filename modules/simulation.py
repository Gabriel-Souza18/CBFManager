import pandas as pd
import numpy as np
from scipy.stats import poisson

def calculate_strength_params(match_data):
    """Calcula os parâmetros de força de ataque e defesa para cada equipe."""
    if match_data.empty:
        return None

    avg_home_goals = match_data['gols_casa'].mean()
    avg_away_goals = match_data['gols_visitante'].mean()

    team_strength = {}
    teams = pd.concat([match_data['equipe_casa'], match_data['equipe_visitante']]).unique()

    for team in teams:
        home_matches = match_data[match_data['equipe_casa'] == team]
        away_matches = match_data[match_data['equipe_visitante'] == team]

        # Força de ataque
        home_attack = (home_matches['gols_casa'].mean() / avg_home_goals) if not home_matches.empty and avg_home_goals > 0 else 1.0
        away_attack = (away_matches['gols_visitante'].mean() / avg_away_goals) if not away_matches.empty and avg_away_goals > 0 else 1.0

        # Força de defesa
        home_defense = (home_matches['gols_visitante'].mean() / avg_away_goals) if not home_matches.empty and avg_away_goals > 0 else 1.0
        away_defense = (away_matches['gols_casa'].mean() / avg_home_goals) if not away_matches.empty and avg_home_goals > 0 else 1.0
        
        team_strength[team] = {
            'home_attack': home_attack, 'away_attack': away_attack,
            'home_defense': home_defense, 'away_defense': away_defense
        }

    return {'avg_home_goals': avg_home_goals, 'avg_away_goals': avg_away_goals, 'team_strength': team_strength}

def predict_expected_goals(home_team, away_team, strength_params):
    """Prevê o número esperado de gols (lambda) para cada equipe na partida."""
    if not strength_params or home_team not in strength_params['team_strength'] or away_team not in strength_params['team_strength']:
        return 1.0, 1.0 # Valores padrão se os dados forem insuficientes

    home_strength = strength_params['team_strength'][home_team]
    away_strength = strength_params['team_strength'][away_team]

    lambda_home = home_strength['home_attack'] * away_strength['away_defense'] * strength_params['avg_home_goals']
    lambda_away = away_strength['away_attack'] * home_strength['home_defense'] * strength_params['avg_away_goals']

    return lambda_home, lambda_away

def simulate_match(lambda_home, lambda_away, max_goals=10):
    """Cria uma matriz de probabilidade de placares usando a Distribuição de Poisson."""
    prob_home = [poisson.pmf(i, lambda_home) for i in range(max_goals + 1)]
    prob_away = [poisson.pmf(i, lambda_away) for i in range(max_goals + 1)]
    
    # Normalizar para garantir que a soma seja 1
    prob_home = np.array(prob_home) / np.sum(prob_home)
    prob_away = np.array(prob_away) / np.sum(prob_away)
    
    prob_matrix = np.outer(prob_home, prob_away)
    return prob_matrix

def calculate_outcome_probabilities(prob_matrix):
    """Calcula as probabilidades de vitória, empate e derrota a partir da matriz."""
    home_win_prob = np.sum(np.tril(prob_matrix, k=-1))
    draw_prob = np.sum(np.diag(prob_matrix))
    away_win_prob = np.sum(np.triu(prob_matrix, k=1))
    
    # Normalizar para garantir que a soma seja 100%
    total_prob = home_win_prob + draw_prob + away_win_prob
    if total_prob > 0:
        home_win_prob /= total_prob
        draw_prob /= total_prob
        away_win_prob /= total_prob

    return home_win_prob, draw_prob, away_win_prob
