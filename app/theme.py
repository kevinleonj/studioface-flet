"""StudioFace Dark Premium Theme — matching production studioface.app"""


class StudioFaceTheme:
    """Dark premium theme with gold/amber accents."""

    # === BACKGROUNDS ===
    BG_PRIMARY = "#131314"
    BG_SURFACE = "#1C1B1C"
    BG_SURFACE_HIGH = "#2A2A2B"
    BG_SURFACE_HIGHEST = "#353436"
    BG_SURFACE_LOW = "#0E0E0F"

    # === PRIMARY (Gold/Amber) ===
    PRIMARY = "#FFC174"
    PRIMARY_BRIGHT = "#FFB95F"
    PRIMARY_CONTAINER = "#F59E0B"
    PRIMARY_DARK = "#855300"
    ON_PRIMARY = "#472A00"

    # === LEGACY ALIASES (for i18n test compatibility) ===
    BACKGROUND = "#131314"
    SURFACE = "#1C1B1C"
    SECONDARY = "#F59E0B"
    ERROR = "#EF4444"
    SUCCESS = "#22C55E"

    # === TEXT ===
    TEXT_PRIMARY = "#E5E2E3"
    TEXT_WHITE = "#FFFFFF"
    TEXT_SECONDARY = "#A0A0A0"
    TEXT_MUTED = "#6B6B6B"
    TEXT_DISABLED = "#555555"
    TEXT_ON_PRIMARY = "#FFFFFF"
    TEXT_ON_SECONDARY = "#FFFFFF"
    TEXT_ON_DARK = "#D8C3AD"

    # === BORDERS ===
    BORDER = "#2A2A2B"
    BORDER_LIGHT = "#3A393A"
    DIVIDER = "#1F1F20"
    OUTLINE = "#3A393A"
    OUTLINE_VARIANT = "#2A2A2B"

    # === BUTTONS ===
    BUTTON_PRIMARY_BG = "#F59E0B"
    BUTTON_TEXT = "#472A00"
    BUTTON_OUTLINE = "#3A393A"

    # === SPACING (4px grid) ===
    SPACE_XS = 4
    SPACE_SM = 8
    SPACE_MD = 16
    SPACE_LG = 24
    SPACE_XL = 32
    SPACE_XXL = 48
    SPACE_HERO = 64
    SPACE_SECTION = 96

    # === BORDER RADIUS ===
    RADIUS_SM = 8
    RADIUS_MD = 12
    RADIUS_LG = 16
    RADIUS_XL = 24
    RADIUS_PILL = 100

    # === TYPOGRAPHY ===
    FONT_HERO = 56
    FONT_H1 = 40
    FONT_H2 = 32
    FONT_H3 = 24
    FONT_H4 = 20
    FONT_BODY = 16
    FONT_BODY_LG = 18
    FONT_CAPTION = 14
    FONT_SMALL = 12
    FONT_LABEL = 11

    # === LAYOUT ===
    MAX_WIDTH = 1200
    NAV_HEIGHT = 64
    CARD_ELEVATION = 0
    CARD_PADDING = 24
    CONTENT_PADDING = 24
    MOBILE_PADDING = 16
    MOBILE_MAX = 600
    TABLET_MAX = 1024

    # === STYLE COLORS + ICONS ===
    STYLE_COLORS = {
        "corporate": "#1E40AF",
        "medical": "#0891B2",
        "banking": "#1E3A5F",
        "startup": "#F59E0B",
        "casual": "#16A34A",
        "tech": "#7C3AED",
    }
    STYLE_ICONS = {
        "corporate": "business_center",
        "medical": "local_hospital",
        "banking": "account_balance",
        "startup": "rocket_launch",
        "casual": "emoji_people",
        "tech": "computer",
    }

    # === SAMPLE HEADSHOT URLS ===
    SAMPLE_PHOTOS = [
        {"name": "Miguel", "url": "https://lh3.googleusercontent.com/aida-public/AB6AXuB_W6FyboLg_EdzIjnYg4r0iF8KjlEpN5OQdnm2X_UTiiXj_Q8MjAkoQEQqPg6BbtFm2Z6bdD133nGouPyAi1bKLod_Mrk2azLfG_-cxR6S1w9tDhE1OfM_XGFZyPVRTyNvM0jjWorOOciSCJUyk_BzNquK3_8fBV6V7-rZzQILAT2FQd4Ec1E52q9rAbiUA0vgApPvREPNIOSOrSl8bCYruNMVJkAJRub53ldV_d0zhCKrAHyV9IzAWuqHaUuvASLgcD52yz2nkOU"},
        {"name": "Juan", "url": "https://lh3.googleusercontent.com/aida-public/AB6AXuD6DCyRDNHDxF02oRVyBZ_WqBwDN2gcEipc3Hh8PLcsCMbeikz8q-ilyHf3d2aqPyI8zRZIXTcePcNVJJsuv0PDe3X02YiAHnoJjWf4pKbV-wSSHKjuHOZI1PclbE5cxVStHmDnXZ1PqvGRJPYC4yEplZsLTIfMTQDqRxisnoh9G005aHt0e_fCJ9xiCk4Psz6sCkicOa0qIUYXFOdEpwwLk0ItFhAlllQqd3WL2TuqsZvldXmSe832dDJiVcBnVEMgRLhdxfhbkEE"},
        {"name": "Filippo", "url": "https://lh3.googleusercontent.com/aida-public/AB6AXuBVq-QDQ2X-nUi_4CK4gQ05c0ZGUV80bXllbbgJrNWYAQgPs2TA8wPslLhEsXkpYJiPA95luAlAXbbCh_CTYeWgrxlLPJ1Sw11LXnhhy0K40cY4JCnK4N96_xTxsyJwozDynwp9AfyTV6CjUuM6KQWpM9XRoII2XreKOkkHLHMxv0L5wgzsH6MNx1iap09HZZXDn0OOmq-ZuLpnuoHzDqyMAGcVafR9vfOXj0lMmMPmAh3oDlNifD11xUVVS7K1eWYnJEeZwiVcX2o"},
        {"name": "Maggie", "url": "https://lh3.googleusercontent.com/aida-public/AB6AXuC70xiUlx6P3CO9yrCYhNIlVedU-lqPQtDfaHP9NL4eej9MMDgk9FNDRoloUXmwu6RDIssbSeh0qvckqacOlm9jzomL48BY41B0ud2MqYQukSIJjxxEZ0Mb69XPd-uWqnJMQ8eB67h41_T-sOBufXAtMPjVVL1MQwwYc3FzU3Xc_iO4LVhMnWXsq1RkfiEclA1kcB48y-wPtpRZoM_ad-uAtqRjNYWUeQCX6vJSbz1S35L87IuY_U1dEhjtxaFsrgi6yUUW4rl3MAk"},
        {"name": "Anita", "url": "https://lh3.googleusercontent.com/aida-public/AB6AXuABMRB2BB_WdGThAsbvhT4p1uWo-mmP5cZ_lG9DnzIiFHTrlRMmaU3_zk8gXQu4-b0hyJ70PwLKkrQAgcmuaW14cGvSZGKETTNo2FnTFWQMAUWesHB7eMfsRWSakCzCutYkuvDP66ruvn2On_p_Jca-OVGhWz5HW1HKU2l3EUPuAuekyy3TAuGL03lcsG0k3TwooTiGeU8HPO_WbdJstb-hVyD3MbVfQLHCwYvnkNCmY3r1KcTr56fshh2wniGyIbfultWNILi3eow"},
    ]

    STYLE_PHOTOS = {
        "corporate": "https://lh3.googleusercontent.com/aida-public/AB6AXuD5uPWM1eCW8DJEQ7ht_WcY7JHN5nmc4L18l4HTUbvkMm1S67-FrniOderai0C5vIrDOiz12xLpT9igLysEKKAZjKUs-Y_xkqh7R4figYX229UAKGB5ukWX044TrNfMPL0Dgvs37TvBUwe4Yco17OMiNY_iXN-y16FqZ8V2jUSm32Zl6mCWr7n8TawClBFm6ScPxiFxfSxrO23FOaJECBw52_ib7NoBtTZUBukkfbL6DHBLNz_HYc56vXXlzXbtTdA3G7EciHawUPA",
        "startup": "https://lh3.googleusercontent.com/aida-public/AB6AXuDG1DkPiDKNde-A1ffzfRS8w4qVkYXeIt1lkp0K3d6VHDutYkyCzOPGKt2yrVSlsDnZ7PI_AUrD56bxMkFz7yKFEj_xr196X-etkUR-SRBpdDoox4Azj_-w_jor_E65OsOuKRvwT5b1_Ge18BrdVbuQguivu12IFlVLZ6NZwbEbEIpocvVabQ0IxN9WOAppFeAEiQre0_-_GXTNMwGU_hGg0QDddLs12ChRqWEmrphWj0oSks5FzgnqfB3EfxfM4a4TKs0NaM1Fsdk",
        "tech": "https://lh3.googleusercontent.com/aida-public/AB6AXuByT3eCJRN1qt-OK0OOU5BJN9ROKaZOONvqIwMMfESpeb9ivzkswtWegmWcDAf8nVmPdMQcQ6ZHQkreuyR-WkxVeHngg48cUoklcpcwIYLq67VJ_me_4rCIbfuxnYT2HcVs38LxNwwkUvUSJdv_b7u6qVRihnjEpWNlnLdait7rcFCJnpg8I5C_cDOfUMz4KJpm875JTZ55MxEuoPTgFcXk_MNVEHg_9uIeYMinatBA3r7kuLnTKdOcdXn_mYU74p3AaYoqvJU4FoQ",
        "banking": "https://lh3.googleusercontent.com/aida-public/AB6AXuDQ4V4KuETchKdkd-cMlJxmwpSFPyq0y5eRuFBlsOJ_3LbSNUKAKRCakmiIB7ijbnf0iEuRZujVRtJyw3TE7oBk_lvRNalaAPIL7O3UhfIEFbuE6JPzxQXuQD2Z1szyZ62SukT6tnh3JXpxk6Ki65XVVe-5_ecL11JQNbrLyLWeSNSXgsLNZHNxAO_qrJ6gplCRf5MpJ1etkQBQUqSWJD-aB6ODZGEPPdQBNYbc18tdUB2OK_P3S8o8yuRM_4KNsENpKSHnkPrnoBE",
        "medical": "https://lh3.googleusercontent.com/aida-public/AB6AXuCaYjaQDhXMTPE1Nmz_m__Ryj1yeMvqOO3OGT_inx8JJTX4bXfvxIPDs5UGsBAp7aVdPdT4HlWAfu5eELD3fA4aZYp75CyIE9JBxFZHsDR2ZcE9L8TtxJMDuDGw1GNsNYJCn5j6d_xPLR6EugJxajPuUl9HrNOMaBzYubyRgb5JJEy3BDkYtD7wPr7JXkyAqjNMucIJWf83kzw0JgIvF0uy5HOA1eJUkAkDosRxd64Xkveuw9PQh4A8tGnn_psODi_DUsrR5hOfP7w",
        "casual": "https://lh3.googleusercontent.com/aida-public/AB6AXuA-FN-NK1M_v7pZRJMZBfXDjxAetTtpxkU0zrW2wzw25Do0mqx5cEHa3dJo-nEOMqBg2OeocAyvUowlB_Lk8Gln5b4zgNPVELcS7V-u5hE3DSm1R7j5bVB_JqMPCRRdW4bj90Dgkgg-IFVscrgufx7HCToEaAky-Q3j3qa8ZiXRgkTpUhMGO4n6ni5_3bXpj0TTgKSwHVDR9qLvgc6JMqG_X21slYitxWgTPMXJ0ly8vkFYDI8zwcaq3MyyH6q_mlyFVGJqD98OWAY",
    }
