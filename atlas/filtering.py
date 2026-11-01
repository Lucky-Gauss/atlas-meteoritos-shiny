"""Filtros compartidos por mapa, indicadores, gráficos, tabla y descarga."""
import pandas as pd


def select_records(df, years, mass_range, conditions, classes=(), query='', include_unknown_year=True,
                   include_unknown_mass=True, include_zero=True, geography='all'):
    """Los rangos numéricos incluyen extremos y las categorías se intersectan."""
    if years[0] > years[1] or mass_range[0] > mass_range[1] or mass_range[0] < 0:
        return df.iloc[0:0].copy()
    mask = df['fall'].isin(conditions)
    valid_year = df['year_valid'] & df['year'].between(*years)
    mask &= valid_year | ((~df['year_valid']) & include_unknown_year)
    valid_mass = df['mass_g'].between(*mass_range) & df['mass_g'].gt(0)
    if include_zero and mass_range[0] == 0:
        valid_mass |= df['mass_g'].eq(0)
    if include_unknown_mass:
        valid_mass |= df['mass_g'].isna()
    mask &= valid_mass
    if classes:
        mask &= df['recclass'].isin(classes)
    if query.strip():
        mask &= df['name'].str.contains(query.strip(), case=False, regex=False, na=False)
    if geography == 'valid':
        mask &= df['map_valid']
    elif geography == 'missing':
        mask &= ~df['map_valid']
    return df.loc[mask].copy()


def export_frame(df):
    """Exporta unidades y banderas explícitas, manteniendo coordenadas originales."""
    cols = ['name', 'id', 'recclass', 'fall', 'year', 'mass_g', 'lat', 'lon', 'map_valid', 'year_valid']
    out = df[cols].copy()
    out['fall'] = out['fall'].map({'Fell': 'Caída observada', 'Found': 'Hallazgo'})
    out.columns = ['Nombre', 'Identificador', 'Clase', 'Condición', 'Año del catálogo', 'Masa (g)',
                   'Latitud original', 'Longitud original', 'Ubicación utilizable', 'Año utilizable']
    return out
