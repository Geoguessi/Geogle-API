class SectionDivider:
    nest_div_pattern = r'<div.*?>.*?<\/div>.*?'

    recommendation_pattern: str = r'<div class="place-card-item Province_recommended-item[^"]*"[^"]*>(.*?)<\/div>'
    foodie_pattern: str = fr'<div class="Province_foodie-image[^"]*"[^"]*>(.*?{nest_div_pattern*2})<\/div>'
    MAIN_ATTRACTION: str = fr'<div class="Province_main-attraction-block[^"]*"[^"]*>(.*?{nest_div_pattern*4})<\/div>'
    ATTRACTION_LIST: str = fr'<div class="col-md-6 col-lg-4"><div class="place-card-item full-width">(.*?)<\/div><\/div>'

class Dashboard:
    RECOMMENDATION = 'recommendation'
    FOODIE = 'foodie'
    ATTRACTION = 'attraction'