"""
Modul Desain Visual dan CSS Kustom untuk Streamlit Dashboard
Menghadirkan UI bertaraf modern, elegan, responsif, dan bernuansa edukatif profesional berlatar cerah (Light Theme).
"""

def get_custom_css() -> str:
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    /* Penguncian Tema Light Mode Global */
    html, body, .stApp, [data-testid="stAppViewContainer"], .main {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: #F8FAFC !important;
        color: #1E293B !important;
    }
    
    [data-testid="stHeader"] {
        background-color: rgba(248, 250, 252, 0.9) !important;
    }
    
    /* Sidebar Aesthetic */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
    }
    
    section[data-testid="stSidebar"] * {
        color: #1E293B !important;
    }
    
    /* Header & Title Styling */
    .app-header {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%) !important;
        border-radius: 16px;
        padding: 24px 30px;
        color: white !important;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .app-header h1 {
        font-size: 1.75rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.025em;
        margin-bottom: 6px;
        background: linear-gradient(135deg, #FFFFFF 0%, #CBD5E1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .app-header p {
        color: #94A3B8 !important;
        font-size: 0.95rem;
        margin: 0;
    }
    
    /* Custom Badge Kategori */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    
    .badge-bb {
        background-color: #FEE2E2 !important;
        color: #DC2626 !important;
        border: 1px solid #FCA5A5;
    }
    
    .badge-mb {
        background-color: #FEF3C7 !important;
        color: #D97706 !important;
        border: 1px solid #FCD34D;
    }
    
    .badge-bsh {
        background-color: #DBEAFE !important;
        color: #2563EB !important;
        border: 1px solid #93C5FD;
    }
    
    .badge-bsb {
        background-color: #D1FAE5 !important;
        color: #059669 !important;
        border: 1px solid #6EE7B7;
    }
    
    /* Card Container */
    .metric-card {
        background: #FFFFFF !important;
        border-radius: 14px;
        padding: 20px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
    }
    
    .metric-title {
        color: #64748B !important;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }
    
    .metric-value {
        color: #0F172A !important;
        font-size: 1.85rem;
        font-weight: 800;
        line-height: 1.2;
    }
    
    .metric-sub {
        color: #94A3B8 !important;
        font-size: 0.8rem;
        margin-top: 4px;
    }
    
    /* Status Disclaimer Banner */
    .disclaimer-banner {
        background: #FFFBEB !important;
        border-left: 4px solid #F59E0B;
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 20px;
        color: #92400E !important;
        font-size: 0.9rem;
    }
    
    .disclaimer-banner strong {
        color: #78350F !important;
    }
    
    .info-banner {
        background: #EFF6FF !important;
        border-left: 4px solid #3B82F6;
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 20px;
        color: #1E40AF !important;
        font-size: 0.9rem;
    }
    
    .success-banner {
        background: #ECFDF5 !important;
        border-left: 4px solid #10B981;
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 20px;
        color: #065F46 !important;
        font-size: 0.9rem;
    }
    
    /* Result Display Card */
    .result-card {
        background: #FFFFFF !important;
        border-radius: 16px;
        padding: 24px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
        text-align: center;
    }
    
    .result-badge {
        font-size: 2.2rem;
        font-weight: 800;
        padding: 12px 30px;
        border-radius: 12px;
        display: inline-block;
        margin: 12px 0;
    }
    
    /* Form Section Header */
    .section-header {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1E293B !important;
        border-bottom: 2px solid #F1F5F9;
        padding-bottom: 8px;
        margin-top: 20px;
        margin-bottom: 16px;
    }
    
    /* Pastikan Text Input & Dropdown memiliki latar terang yang terbaca jelas */
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
    }
    </style>
    """
