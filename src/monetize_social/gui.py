from __future__ import annotations

import csv
from datetime import date
from pathlib import Path
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from monetize_social.affiliate_pipeline import PipelinePaths, ensure_onboarding_packets, run_pipeline
from monetize_social.campaigns import (
    collect_seed_terms,
    generate_ad_captions,
    generate_hashtags,
    write_campaign_export,
)
from monetize_social.prefs import get_pref, set_pref
from monetize_social.procedure import load_procedures
from monetize_social.sponsor_ops import (
    add_utm,
    build_dashboard_rows,
    build_followup_rows,
    build_roi_rows,
    compute_total_score,
    dedupe_rows,
    infer_program_urls,
    normalize_sponsor_name,
    write_csv,
    write_kanban_markdown,
)


SPONSOR_TRACKER_HEADERS = [
    "Sponsor",
    "Website",
    "Vertical",
    "Program/Partnership Page",
    "Application Form URL",
    "Application Method",
    "Program Type (Sponsorship/Affiliate/Both)",
    "Estimated Investment Amount (USD)",
    "Region Availability",
    "Audience Minimum",
    "Traffic/Engagement Requirement",
    "Content/Niche Requirement",
    "Required Assets",
    "Compliance Notes",
    "Decision Maker/Team Contact",
    "Fit Score (1-5)",
    "Readiness Score (1-5)",
    "Access Score (1-5)",
    "Status",
    "Last Verified Date",
    "Notes",
]

PRIORITY_SPONSORS = [
    {
        "Sponsor": "Black Diamond Equipment",
        "Website": "https://www.blackdiamondequipment.com/",
        "Program Type (Sponsorship/Affiliate/Both)": "Both",
        "Estimated Investment Amount (USD)": "500",
        "Status": "Lead",
    },
    {
        "Sponsor": "Lenovo",
        "Website": "https://www.lenovo.com/",
        "Program Type (Sponsorship/Affiliate/Both)": "Both",
        "Estimated Investment Amount (USD)": "1500",
        "Status": "Lead",
    },
    {
        "Sponsor": "Mining Gear Partners (Category)",
        "Program Type (Sponsorship/Affiliate/Both)": "Both",
        "Estimated Investment Amount (USD)": "700",
        "Status": "Lead",
    },
    {
        "Sponsor": "Colombia Partners (Tourism/Outdoor)",
        "Program Type (Sponsorship/Affiliate/Both)": "Both",
        "Estimated Investment Amount (USD)": "400",
        "Region Availability": "Colombia/LatAm",
        "Status": "Lead",
    },
    {
        "Sponsor": "Amazon",
        "Website": "https://www.amazon.com/",
        "Program Type (Sponsorship/Affiliate/Both)": "Both",
        "Estimated Investment Amount (USD)": "1200",
        "Status": "Lead",
    },
    {
        "Sponsor": "Sony",
        "Website": "https://www.sony.com/",
        "Program Type (Sponsorship/Affiliate/Both)": "Both",
        "Estimated Investment Amount (USD)": "1800",
        "Status": "Lead",
    },
    {
        "Sponsor": "Pioneer",
        "Website": "https://www.pioneer.com/",
        "Program Type (Sponsorship/Affiliate/Both)": "Both",
        "Estimated Investment Amount (USD)": "1000",
        "Status": "Lead",
    },
    {
        "Sponsor": "JL Audio",
        "Website": "https://www.jlaudio.com/",
        "Program Type (Sponsorship/Affiliate/Both)": "Both",
        "Estimated Investment Amount (USD)": "1100",
        "Status": "Lead",
    },
    {
        "Sponsor": "Kenwood",
        "Website": "https://www.kenwood.com/",
        "Program Type (Sponsorship/Affiliate/Both)": "Both",
        "Estimated Investment Amount (USD)": "900",
        "Status": "Lead",
    },
    {
        "Sponsor": "Fluke",
        "Website": "https://www.fluke.com/",
        "Program Type (Sponsorship/Affiliate/Both)": "Both",
        "Estimated Investment Amount (USD)": "950",
        "Status": "Lead",
    },
    {
        "Sponsor": "Google",
        "Website": "https://about.google/",
        "Program Type (Sponsorship/Affiliate/Both)": "Both",
        "Estimated Investment Amount (USD)": "2000",
        "Status": "Lead",
    },
    {
        "Sponsor": "AWS",
        "Website": "https://aws.amazon.com/",
        "Program Type (Sponsorship/Affiliate/Both)": "Both",
        "Estimated Investment Amount (USD)": "2200",
        "Status": "Lead",
    },
    {
        "Sponsor": "Subaru Racing",
        "Website": "https://www.subaru.com/",
        "Program Type (Sponsorship/Affiliate/Both)": "Both",
        "Estimated Investment Amount (USD)": "1600",
        "Status": "Lead",
    },
    {
        "Sponsor": "Blue-Point",
        "Website": "https://www.blue-point.com/",
        "Program Type (Sponsorship/Affiliate/Both)": "Both",
        "Estimated Investment Amount (USD)": "900",
        "Status": "Lead",
    },
    {
        "Sponsor": "Snap-on",
        "Website": "https://www.snapon.com/",
        "Program Type (Sponsorship/Affiliate/Both)": "Both",
        "Estimated Investment Amount (USD)": "1300",
        "Status": "Lead",
    },
    {
        "Sponsor": "Borla",
        "Website": "https://www.borla.com/",
        "Program Type (Sponsorship/Affiliate/Both)": "Both",
        "Estimated Investment Amount (USD)": "1000",
        "Status": "Lead",
    },
    {
        "Sponsor": "Carhartt",
        "Website": "https://www.carhartt.com/",
        "Program Type (Sponsorship/Affiliate/Both)": "Both",
        "Estimated Investment Amount (USD)": "1200",
        "Status": "Lead",
    },
    {
        "Sponsor": "Polaris",
        "Website": "https://www.polaris.com/",
        "Program Type (Sponsorship/Affiliate/Both)": "Both",
        "Estimated Investment Amount (USD)": "1400",
        "Status": "Lead",
    },
    {
        "Sponsor": "Ski-Doo",
        "Website": "https://www.ski-doo.com/",
        "Program Type (Sponsorship/Affiliate/Both)": "Both",
        "Estimated Investment Amount (USD)": "1400",
        "Status": "Lead",
    },
    {
        "Sponsor": "Kicker Audio",
        "Website": "https://www.kicker.com/",
        "Program Type (Sponsorship/Affiliate/Both)": "Both",
        "Estimated Investment Amount (USD)": "1100",
        "Status": "Lead",
    },
    {
        "Sponsor": "Porsche Motorsport",
        "Website": "https://www.porsche.com/",
        "Program Type (Sponsorship/Affiliate/Both)": "Both",
        "Estimated Investment Amount (USD)": "2400",
        "Status": "Lead",
    },
    {
        "Sponsor": "Ford Performance (Mustang)",
        "Website": "https://performance.ford.com/",
        "Program Type (Sponsorship/Affiliate/Both)": "Both",
        "Estimated Investment Amount (USD)": "1700",
        "Status": "Lead",
    },
    {
        "Sponsor": "Chevrolet Performance",
        "Website": "https://www.chevrolet.com/performance",
        "Program Type (Sponsorship/Affiliate/Both)": "Both",
        "Estimated Investment Amount (USD)": "1700",
        "Status": "Lead",
    },
    {
        "Sponsor": "Ducati",
        "Website": "https://www.ducati.com/",
        "Program Type (Sponsorship/Affiliate/Both)": "Both",
        "Estimated Investment Amount (USD)": "1800",
        "Status": "Lead",
    },
    {
        "Sponsor": "KTM",
        "Website": "https://www.ktm.com/",
        "Program Type (Sponsorship/Affiliate/Both)": "Both",
        "Estimated Investment Amount (USD)": "1600",
        "Status": "Lead",
    },
    {
        "Sponsor": "Boston Whaler",
        "Website": "https://www.bostonwhaler.com/",
        "Program Type (Sponsorship/Affiliate/Both)": "Both",
        "Estimated Investment Amount (USD)": "1900",
        "Status": "Lead",
    },
    {
        "Sponsor": "Cigarette Racing",
        "Website": "https://www.cigaretteracing.com/",
        "Program Type (Sponsorship/Affiliate/Both)": "Both",
        "Estimated Investment Amount (USD)": "2000",
        "Status": "Lead",
    },
    {
        "Sponsor": "Donzi Marine",
        "Website": "https://www.donzimarine.com/",
        "Program Type (Sponsorship/Affiliate/Both)": "Both",
        "Estimated Investment Amount (USD)": "1600",
        "Status": "Lead",
    },
    {
        "Sponsor": "Milwaukee Tool",
        "Website": "https://www.milwaukeetool.com/",
        "Program Type (Sponsorship/Affiliate/Both)": "Both",
        "Estimated Investment Amount (USD)": "1200",
        "Status": "Lead",
    },
    {
        "Sponsor": "Garmin",
        "Website": "https://www.garmin.com/",
        "Program Type (Sponsorship/Affiliate/Both)": "Both",
        "Estimated Investment Amount (USD)": "1800",
        "Status": "Lead",
    },
]


class MonetizeSocialGUI:
    def __init__(self, root: tk.Tk, project_root: Path) -> None:
        self.root = root
        self.project_root = project_root
        self.paths = PipelinePaths(root=project_root)

        self.root.title("MonetizeSocial - Affiliate Operations")
        self.root.geometry("1080x760")
        self.root.minsize(900, 620)

        self.status_text = tk.StringVar(value="Ready")
        self.summary_text = tk.StringVar(value="Run the pipeline to generate dashboard and workbook outputs.")
        self.campaign_tone = tk.StringVar(value="Direct")
        self._pipeline_running = False
        self._pipeline_buttons: list[ttk.Button] = []
        self._check_states: dict[str, list[tk.BooleanVar]] = {}
        self.sponsor_budget_var = tk.StringVar(value=str(get_pref("sponsor_budget_usd", "1000")))
        self.sponsor_affordable_only_var = tk.BooleanVar(value=bool(get_pref("sponsor_affordable_only", False)))
        self.sponsor_vertical_filter_var = tk.StringVar(value=str(get_pref("sponsor_vertical_filter", "All")))
        self.sponsor_weight_fit_var = tk.StringVar(value=str(get_pref("sponsor_weight_fit", "2")))
        self.sponsor_weight_readiness_var = tk.StringVar(value=str(get_pref("sponsor_weight_readiness", "1")))
        self.sponsor_weight_access_var = tk.StringVar(value=str(get_pref("sponsor_weight_access", "1")))
        self.sponsor_weight_budget_var = tk.StringVar(value=str(get_pref("sponsor_weight_budget", "2")))
        self.sponsor_weight_form_var = tk.StringVar(value=str(get_pref("sponsor_weight_form", "1")))

        self._build_layout()
        self._load_procedure_tab()
        self._refresh_outputs()

    def _build_layout(self) -> None:
        frame = ttk.Frame(self.root, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)

        header = ttk.Label(frame, text="Affiliate Program Control Center", font=("TkDefaultFont", 14, "bold"))
        header.pack(anchor=tk.W, pady=(0, 8))

        tabs = ttk.Notebook(frame)
        tabs.pack(fill=tk.BOTH, expand=True)

        self.procedure_tab = ttk.Frame(tabs, padding=10)
        self.pipeline_tab = ttk.Frame(tabs, padding=10)
        self.campaign_tab = ttk.Frame(tabs, padding=10)
        self.sponsors_tab = ttk.Frame(tabs, padding=10)
        self.outputs_tab = ttk.Frame(tabs, padding=10)

        tabs.add(self.procedure_tab, text="Procedure")
        tabs.add(self.pipeline_tab, text="Pipeline")
        tabs.add(self.campaign_tab, text="Hashtag Ads")
        tabs.add(self.sponsors_tab, text="Sponsors")
        tabs.add(self.outputs_tab, text="Outputs")

        self._build_procedure_layout()
        self._build_pipeline_layout()
        self._build_campaign_layout()
        self._build_sponsors_layout()
        self._build_outputs_layout()

        status = ttk.Label(frame, textvariable=self.status_text)
        status.pack(fill=tk.X, pady=(8, 0))

    def _build_procedure_layout(self) -> None:
        self.procedure_title = tk.StringVar(value="")

        title = ttk.Label(self.procedure_tab, textvariable=self.procedure_title, font=("TkDefaultFont", 12, "bold"))
        title.pack(anchor=tk.W, pady=(0, 8))

        picker_frame = ttk.Frame(self.procedure_tab)
        picker_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(picker_frame, text="Workflow:").pack(side=tk.LEFT)
        self.procedure_selector = ttk.Combobox(picker_frame, state="readonly", width=40)
        self.procedure_selector.pack(side=tk.LEFT, padx=8)
        self.procedure_selector.bind("<<ComboboxSelected>>", self._on_procedure_selected)

        body = ttk.Frame(self.procedure_tab)
        body.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(body, highlightthickness=0)
        scrollbar = ttk.Scrollbar(body, orient=tk.VERTICAL, command=self.canvas.yview)
        self.steps_frame = ttk.Frame(self.canvas)

        self.steps_frame.bind("<Configure>", lambda _: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.create_window((0, 0), window=self.steps_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _build_pipeline_layout(self) -> None:
        actions = ttk.Frame(self.pipeline_tab)
        actions.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(actions, text="Run Full Build", command=self._run_pipeline).pack(side=tk.LEFT, padx=8)
        ttk.Button(actions, text="Create Onboarding Packets", command=self._create_packets).pack(side=tk.LEFT, padx=8)
        ttk.Button(actions, text="Refresh Outputs", command=self._refresh_outputs).pack(side=tk.LEFT, padx=8)

        # keep references so they can be disabled during a run
        for btn in actions.winfo_children():
            if isinstance(btn, ttk.Button):
                self._pipeline_buttons.append(btn)

        summary_group = ttk.LabelFrame(self.pipeline_tab, text="Latest Build Summary", padding=10)
        summary_group.pack(fill=tk.BOTH, expand=True)

        self.summary_label = ttk.Label(summary_group, textvariable=self.summary_text, justify=tk.LEFT)
        self.summary_label.pack(fill=tk.BOTH, expand=True, anchor=tk.NW)

    def _build_campaign_layout(self) -> None:
        intro = ttk.Label(
            self.campaign_tab,
            text="Collect affiliate signals from your master sheet and generate hashtag-ready ad captions.",
        )
        intro.pack(anchor=tk.W, pady=(0, 8))

        form = ttk.Frame(self.campaign_tab)
        form.pack(fill=tk.X, pady=(0, 8))

        self.niche_entry = ttk.Entry(form)
        self.offer_entry = ttk.Entry(form)
        self.audience_entry = ttk.Entry(form)

        ttk.Label(form, text="Niche").grid(row=0, column=0, sticky="w")
        ttk.Label(form, text="Offer").grid(row=0, column=1, sticky="w")
        ttk.Label(form, text="Audience").grid(row=0, column=2, sticky="w")

        self.niche_entry.grid(row=1, column=0, sticky="ew", padx=(0, 6))
        self.offer_entry.grid(row=1, column=1, sticky="ew", padx=(0, 6))
        self.audience_entry.grid(row=1, column=2, sticky="ew")

        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)
        form.columnconfigure(2, weight=1)

        tone_row = ttk.Frame(self.campaign_tab)
        tone_row.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(tone_row, text="Tone").pack(side=tk.LEFT)

        tone_picker = ttk.Combobox(
            tone_row,
            textvariable=self.campaign_tone,
            values=["Direct", "Educational", "Story"],
            width=16,
            state="readonly",
        )
        tone_picker.pack(side=tk.LEFT, padx=(8, 12))

        ttk.Button(tone_row, text="Collect from Master CSV", command=self._collect_hashtag_seeds).pack(side=tk.LEFT)
        ttk.Button(tone_row, text="Top Sponsors -> Hashtags", command=self._load_top_sponsor_hashtags).pack(side=tk.LEFT, padx=8)
        ttk.Button(tone_row, text="Top Sponsors -> Captions", command=self._load_top_sponsor_campaign).pack(side=tk.LEFT, padx=8)
        ttk.Button(tone_row, text="Generate Hashtag Ads", command=self._generate_campaign).pack(side=tk.LEFT, padx=8)
        ttk.Button(tone_row, text="Export Campaign CSV", command=self._export_campaign).pack(side=tk.LEFT, padx=8)

        content = ttk.Frame(self.campaign_tab)
        content.pack(fill=tk.BOTH, expand=True)

        hashtag_box = ttk.LabelFrame(content, text="Hashtags", padding=8)
        hashtag_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))

        self.hashtag_text = tk.Text(hashtag_box, height=16, wrap=tk.WORD)
        self.hashtag_text.pack(fill=tk.BOTH, expand=True)

        caption_box = ttk.LabelFrame(content, text="Ad Captions", padding=8)
        caption_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 0))

        self.caption_text = tk.Text(caption_box, height=16, wrap=tk.WORD)
        self.caption_text.pack(fill=tk.BOTH, expand=True)

    def _build_outputs_layout(self) -> None:
        ttk.Label(
            self.outputs_tab,
            text="Expected files generated by the pipeline and procedure workflow:",
        ).pack(anchor=tk.W, pady=(0, 8))

        columns = ("file", "status")
        self.outputs_table = ttk.Treeview(self.outputs_tab, columns=columns, show="headings", height=18)
        self.outputs_table.heading("file", text="File")
        self.outputs_table.heading("status", text="Status")
        self.outputs_table.column("file", width=760)
        self.outputs_table.column("status", width=120, anchor=tk.CENTER)
        self.outputs_table.pack(fill=tk.BOTH, expand=True)

        ttk.Button(self.outputs_tab, text="Refresh", command=self._refresh_outputs).pack(anchor=tk.E, pady=(8, 0))

    def _build_sponsors_layout(self) -> None:
        ttk.Label(
            self.sponsors_tab,
            text="Track sponsor discovery, forms, and qualification requirements in one place.",
        ).pack(anchor=tk.W, pady=(0, 8))

        settings = ttk.LabelFrame(self.sponsors_tab, text="Budget Settings", padding=8)
        settings.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(settings, text="Available Investment (USD)").grid(row=0, column=0, sticky="w")
        budget_entry = ttk.Entry(settings, textvariable=self.sponsor_budget_var, width=16)
        budget_entry.grid(row=1, column=0, sticky="w", padx=(0, 8))

        affordable_check = ttk.Checkbutton(
            settings,
            text="Show affordable sponsors only",
            variable=self.sponsor_affordable_only_var,
            command=self._refresh_sponsors,
        )
        affordable_check.grid(row=1, column=1, sticky="w", padx=(0, 8))

        ttk.Label(settings, text="Vertical Filter").grid(row=0, column=2, sticky="w")
        vertical_filter = ttk.Combobox(
            settings,
            textvariable=self.sponsor_vertical_filter_var,
            values=[
                "All",
                "Auto/Racing",
                "Marine",
                "Motorcycle",
                "Tools",
                "Audio",
                "Outdoor",
                "Computers/Cloud",
                "Flight/Industrial",
            ],
            state="readonly",
            width=20,
        )
        vertical_filter.grid(row=1, column=2, sticky="w", padx=(0, 8))
        vertical_filter.bind("<<ComboboxSelected>>", lambda _: self._refresh_sponsors())

        ttk.Label(settings, text="W Fit").grid(row=0, column=4, sticky="w")
        ttk.Label(settings, text="W Ready").grid(row=0, column=5, sticky="w")
        ttk.Label(settings, text="W Access").grid(row=0, column=6, sticky="w")
        ttk.Label(settings, text="W Budget").grid(row=0, column=7, sticky="w")
        ttk.Label(settings, text="W Form").grid(row=0, column=8, sticky="w")

        ttk.Entry(settings, textvariable=self.sponsor_weight_fit_var, width=4).grid(row=1, column=4, sticky="w")
        ttk.Entry(settings, textvariable=self.sponsor_weight_readiness_var, width=4).grid(row=1, column=5, sticky="w")
        ttk.Entry(settings, textvariable=self.sponsor_weight_access_var, width=4).grid(row=1, column=6, sticky="w")
        ttk.Entry(settings, textvariable=self.sponsor_weight_budget_var, width=4).grid(row=1, column=7, sticky="w")
        ttk.Entry(settings, textvariable=self.sponsor_weight_form_var, width=4).grid(row=1, column=8, sticky="w")

        ttk.Button(settings, text="Save Settings", command=self._save_sponsor_settings).grid(row=1, column=3, sticky="w")

        actions = ttk.Frame(self.sponsors_tab)
        actions.pack(fill=tk.X, pady=(0, 8))

        ttk.Button(actions, text="Refresh Tracker", command=self._refresh_sponsors).pack(side=tk.LEFT)
        ttk.Button(actions, text="Add Priority Targets", command=self._add_priority_sponsors).pack(side=tk.LEFT, padx=8)
        ttk.Button(actions, text="Auto-Discover URLs", command=self._auto_discover_sponsor_urls).pack(side=tk.LEFT, padx=8)
        ttk.Button(actions, text="Export Weekly Bundle", command=self._export_weekly_sponsor_bundle).pack(side=tk.LEFT, padx=8)

        form = ttk.LabelFrame(self.sponsors_tab, text="Add Sponsor Lead", padding=8)
        form.pack(fill=tk.X, pady=(0, 8))

        self.sponsor_name_entry = ttk.Entry(form)
        self.sponsor_website_entry = ttk.Entry(form)
        self.sponsor_form_url_entry = ttk.Entry(form)
        self.sponsor_method_entry = ttk.Entry(form)
        self.sponsor_investment_entry = ttk.Entry(form)
        self.sponsor_region_entry = ttk.Entry(form)
        self.sponsor_vertical_var = tk.StringVar(value="Auto/Racing")
        self.sponsor_vertical_picker = ttk.Combobox(
            form,
            textvariable=self.sponsor_vertical_var,
            values=[
                "Auto/Racing",
                "Marine",
                "Motorcycle",
                "Tools",
                "Audio",
                "Outdoor",
                "Computers/Cloud",
                "Flight/Industrial",
                "Other",
            ],
            state="readonly",
            width=20,
        )

        self.sponsor_fit_entry = ttk.Entry(form, width=8)
        self.sponsor_readiness_entry = ttk.Entry(form, width=8)
        self.sponsor_access_entry = ttk.Entry(form, width=8)

        ttk.Label(form, text="Sponsor").grid(row=0, column=0, sticky="w")
        ttk.Label(form, text="Website").grid(row=0, column=1, sticky="w")
        ttk.Label(form, text="Application Form URL").grid(row=0, column=2, sticky="w")

        self.sponsor_name_entry.grid(row=1, column=0, sticky="ew", padx=(0, 6))
        self.sponsor_website_entry.grid(row=1, column=1, sticky="ew", padx=(0, 6))
        self.sponsor_form_url_entry.grid(row=1, column=2, sticky="ew")

        ttk.Label(form, text="Method").grid(row=2, column=0, sticky="w", pady=(8, 0))
        ttk.Label(form, text="Investment (USD)").grid(row=2, column=1, sticky="w", pady=(8, 0))
        ttk.Label(form, text="Region").grid(row=2, column=2, sticky="w", pady=(8, 0))
        ttk.Label(form, text="Vertical").grid(row=2, column=3, sticky="w", pady=(8, 0))

        self.sponsor_method_entry.grid(row=3, column=0, sticky="ew", padx=(0, 6))
        self.sponsor_investment_entry.grid(row=3, column=1, sticky="ew", padx=(0, 6))
        self.sponsor_region_entry.grid(row=3, column=2, sticky="ew", padx=(0, 6))
        self.sponsor_vertical_picker.grid(row=3, column=3, sticky="ew", padx=(0, 6))

        ttk.Label(form, text="Fit (1-5)").grid(row=4, column=0, sticky="w", pady=(8, 0))
        ttk.Label(form, text="Readiness (1-5)").grid(row=4, column=1, sticky="w", pady=(8, 0))
        ttk.Label(form, text="Access (1-5)").grid(row=4, column=2, sticky="w", pady=(8, 0))

        self.sponsor_fit_entry.grid(row=5, column=0, sticky="w", padx=(0, 6))
        self.sponsor_readiness_entry.grid(row=5, column=1, sticky="w", padx=(0, 6))
        self.sponsor_access_entry.grid(row=5, column=2, sticky="w", padx=(0, 6))

        ttk.Button(form, text="Add Lead", command=self._add_sponsor_lead).grid(row=5, column=3, sticky="e", pady=(8, 0))

        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)
        form.columnconfigure(2, weight=1)
        form.columnconfigure(3, weight=1)

        columns = (
            "Sponsor",
            "Vertical",
            "Application Form URL",
            "Program Type",
            "Investment (USD)",
            "Total Score",
            "Affordable",
            "Status",
            "Last Verified Date",
        )
        self.sponsor_table = ttk.Treeview(self.sponsors_tab, columns=columns, show="headings", height=14)
        self.sponsor_table.heading("Sponsor", text="Sponsor")
        self.sponsor_table.heading("Vertical", text="Vertical")
        self.sponsor_table.heading("Application Form URL", text="Application Form URL")
        self.sponsor_table.heading("Program Type", text="Program Type")
        self.sponsor_table.heading("Investment (USD)", text="Investment (USD)")
        self.sponsor_table.heading("Total Score", text="Total Score")
        self.sponsor_table.heading("Affordable", text="Affordable")
        self.sponsor_table.heading("Status", text="Status")
        self.sponsor_table.heading("Last Verified Date", text="Last Verified")

        self.sponsor_table.column("Sponsor", width=220)
        self.sponsor_table.column("Vertical", width=140, anchor=tk.CENTER)
        self.sponsor_table.column("Application Form URL", width=220)
        self.sponsor_table.column("Program Type", width=140, anchor=tk.CENTER)
        self.sponsor_table.column("Investment (USD)", width=130, anchor=tk.E)
        self.sponsor_table.column("Total Score", width=100, anchor=tk.CENTER)
        self.sponsor_table.column("Affordable", width=100, anchor=tk.CENTER)
        self.sponsor_table.column("Status", width=120, anchor=tk.CENTER)
        self.sponsor_table.column("Last Verified Date", width=130, anchor=tk.CENTER)
        self.sponsor_table.pack(fill=tk.BOTH, expand=True)

    def _load_procedure_tab(self) -> None:
        self.procedures = load_procedures(self.project_root)
        names = list(self.procedures.keys())

        self.procedure_selector["values"] = names
        if names:
            self.procedure_selector.current(0)
            self._render_procedure(names[0])
        self._refresh_sponsors()

    def _on_procedure_selected(self, _: object) -> None:
        selected = self.procedure_selector.get()
        if selected:
            self._render_procedure(selected)

    def _render_procedure(self, title: str) -> None:
        self.procedure_title.set(title)

        # Persist current checkbox states before destroying widgets
        if hasattr(self, "_current_procedure") and self._current_procedure in self._check_states:
            # states already tracked via BooleanVar references — nothing to do
            pass

        for child in self.steps_frame.winfo_children():
            child.destroy()

        self._current_procedure = title
        saved = self._check_states.get(title, [])

        steps = self.procedures.get(title, [])
        self._check_states[title] = []
        for idx, step in enumerate(steps, start=1):
            row = ttk.Frame(self.steps_frame)
            row.pack(fill=tk.X, anchor=tk.W, pady=2)

            initial = saved[idx - 1].get() if idx - 1 < len(saved) else False
            done = tk.BooleanVar(value=initial)
            self._check_states[title].append(done)

            chk = ttk.Checkbutton(row, variable=done)
            chk.pack(side=tk.LEFT)

            label = ttk.Label(row, text=f"{idx}. {step}", wraplength=900, justify=tk.LEFT)
            label.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _run_pipeline(self) -> None:
        if self._pipeline_running:
            return
        self._pipeline_running = True
        for btn in self._pipeline_buttons:
            btn.state(["disabled"])
        self.status_text.set("Running pipeline...")

        def target() -> None:
            try:
                summary = run_pipeline(root=self.project_root, live_link_check=False)
                lines = [
                    "Build completed.",
                    f"- Total programs: {summary['total_programs']}",
                    f"- Avg health score: {summary['avg_health_score']}",
                    f"- Validation issues: {summary['validation_issues']}",
                    f"- Snapshot: {summary['snapshot']}",
                ]
                self.root.after(0, lambda: self.summary_text.set("\n".join(lines)))
                self.root.after(0, self._refresh_outputs)
                self.root.after(0, lambda: self.status_text.set("Pipeline completed successfully."))
            except Exception as exc:  # noqa: BLE001
                self.root.after(0, lambda: self.status_text.set("Pipeline failed."))
                self.root.after(0, lambda: messagebox.showerror("Pipeline Error", str(exc)))
            finally:
                self.root.after(0, self._unlock_pipeline)

        threading.Thread(target=target, daemon=True).start()

    def _unlock_pipeline(self) -> None:
        self._pipeline_running = False
        for btn in self._pipeline_buttons:
            btn.state(["!disabled"])

    def _create_packets(self) -> None:
        try:
            with self.paths.master.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            ensure_onboarding_packets(rows, self.project_root)
            self.status_text.set("Onboarding packets created.")
            self._refresh_outputs()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Packet Error", str(exc))
            self.status_text.set("Failed to create packets.")

    def _collect_hashtag_seeds(self) -> None:
        seeds = collect_seed_terms(self.paths.master)
        hashtags = generate_hashtags(seeds, niche=self.niche_entry.get(), limit=40)
        self.hashtag_text.delete("1.0", tk.END)
        self.hashtag_text.insert(tk.END, " ".join(hashtags))
        self.status_text.set(f"Collected {len(hashtags)} hashtags from master data.")

    def _load_top_sponsor_hashtags(self) -> None:
        try:
            ranked = self._rank_sponsor_rows(self._read_sponsor_rows())
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Sponsor Load Error", str(exc))
            self.status_text.set("Unable to load sponsors for hashtag generation.")
            return

        if not ranked:
            messagebox.showerror(
                "No Sponsor Matches",
                "No sponsors match current filters. Adjust budget/vertical settings in Sponsors tab.",
            )
            return

        top = ranked[:10]
        sponsor_terms = [item["row"].get("Sponsor", "") for item in top if item["row"].get("Sponsor")]
        hashtags = generate_hashtags(sponsor_terms, niche=self.niche_entry.get(), limit=40)

        self.hashtag_text.delete("1.0", tk.END)
        self.hashtag_text.insert(tk.END, " ".join(hashtags))

        # Export traceability report so sponsor selection and hashtags stay linked.
        out_path = self.paths.exports / "top_sponsor_hashtag_plan.csv"
        with out_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["rank", "sponsor", "vertical", "total_score", "investment_usd", "affordable", "hashtag"],
            )
            writer.writeheader()
            for idx, item in enumerate(top, start=1):
                row = item["row"]
                sponsor = row.get("Sponsor", "")
                sponsor_tag = generate_hashtags([sponsor], limit=1)
                writer.writerow(
                    {
                        "rank": idx,
                        "sponsor": sponsor,
                        "vertical": item["vertical"],
                        "total_score": item["total_score"],
                        "investment_usd": item["investment_raw"],
                        "affordable": item["affordable_text"],
                        "hashtag": sponsor_tag[0] if sponsor_tag else "",
                    }
                )

        self._refresh_outputs()
        self.status_text.set(
            f"Loaded hashtags from top {len(top)} sponsors and exported {out_path.relative_to(self.project_root)}"
        )

    def _load_top_sponsor_campaign(self) -> None:
        self._load_top_sponsor_hashtags()
        hashtags = [tag for tag in self.hashtag_text.get("1.0", tk.END).split() if tag.startswith("#")]
        if not hashtags:
            return

        ranked = self._rank_sponsor_rows(self._read_sponsor_rows())
        top_name = ranked[0]["row"].get("Sponsor", "") if ranked else "Top Sponsor"
        if not self.offer_entry.get().strip():
            self.offer_entry.insert(0, top_name)
        if not self.audience_entry.get().strip():
            self.audience_entry.insert(0, "performance and outdoor audience")

        self._generate_campaign()
        self.status_text.set("Loaded top sponsors into hashtags and generated first-draft captions.")

    def _generate_campaign(self) -> None:
        existing = self.hashtag_text.get("1.0", tk.END).strip()
        hashtags = [tag for tag in existing.split() if tag.startswith("#")]
        if not hashtags:
            seeds = collect_seed_terms(self.paths.master)
            hashtags = generate_hashtags(seeds, niche=self.niche_entry.get(), limit=40)

        captions = generate_ad_captions(
            niche=self.niche_entry.get(),
            offer=self.offer_entry.get(),
            audience=self.audience_entry.get(),
            tone=self.campaign_tone.get(),
            hashtags=hashtags,
        )

        self.hashtag_text.delete("1.0", tk.END)
        self.hashtag_text.insert(tk.END, " ".join(hashtags))

        self.caption_text.delete("1.0", tk.END)
        self.caption_text.insert(tk.END, "\n\n".join(captions))
        self.status_text.set("Generated hashtag ads.")

    def _export_campaign(self) -> None:
        hashtags = [tag for tag in self.hashtag_text.get("1.0", tk.END).split() if tag.startswith("#")]
        captions = [line.strip() for line in self.caption_text.get("1.0", tk.END).split("\n\n") if line.strip()]

        if not hashtags or not captions:
            messagebox.showerror("Export Error", "Generate hashtags and captions before exporting.")
            return

        out_path = self.paths.exports / "hashtag_campaign_plan.csv"
        write_campaign_export(out_path, captions=captions, hashtags=hashtags)
        self.status_text.set(f"Campaign exported: {out_path.relative_to(self.project_root)}")
        self._refresh_outputs()

    def _refresh_outputs(self) -> None:
        output_files = [
            self.paths.priority_csv,
            self.paths.payout_csv,
            self.paths.dashboard_csv,
            self.paths.validation_csv,
            self.paths.workbook,
            self.paths.changelog,
            self.paths.exports / "hashtag_campaign_plan.csv",
            self.paths.exports / "top_sponsor_hashtag_plan.csv",
            self.paths.exports / "top_sponsors_this_week.csv",
            self.paths.exports / "sponsor_followup_sequence.csv",
            self.paths.exports / "sponsor_attribution_pack.csv",
            self.paths.exports / "sponsor_roi_model.csv",
            self.paths.exports / "sponsor_kanban_board.md",
            self.paths.exports / "sponsor_dashboard_summary.csv",
            self.project_root / "docs/onboarding_packets",
        ]

        for row_id in self.outputs_table.get_children():
            self.outputs_table.delete(row_id)

        for output in output_files:
            status = "Present" if output.exists() else "Missing"
            rel_path = output.relative_to(self.project_root)
            self.outputs_table.insert("", tk.END, values=(str(rel_path), status))

    def _sponsor_tracker_path(self) -> Path:
        return self.project_root / "data/templates/sponsor_discovery_tracker.csv"

    def _score_weights(self) -> dict[str, int]:
        return {
            "fit": max(1, self._parse_int(self.sponsor_weight_fit_var.get(), 2)),
            "readiness": max(1, self._parse_int(self.sponsor_weight_readiness_var.get(), 1)),
            "access": max(1, self._parse_int(self.sponsor_weight_access_var.get(), 1)),
            "budget": max(1, self._parse_int(self.sponsor_weight_budget_var.get(), 2)),
            "form": max(1, self._parse_int(self.sponsor_weight_form_var.get(), 1)),
        }

    def _ensure_sponsor_tracker(self) -> None:
        tracker_path = self._sponsor_tracker_path()
        if tracker_path.exists():
            return
        tracker_path.parent.mkdir(parents=True, exist_ok=True)
        with tracker_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=SPONSOR_TRACKER_HEADERS)
            writer.writeheader()

    def _read_sponsor_rows(self) -> list[dict[str, str]]:
        self._ensure_sponsor_tracker()
        tracker_path = self._sponsor_tracker_path()
        with tracker_path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        normalized, _ = dedupe_rows(rows, SPONSOR_TRACKER_HEADERS)
        return normalized

    def _write_sponsor_rows(self, rows: list[dict[str, str]]) -> None:
        tracker_path = self._sponsor_tracker_path()
        normalized, _ = dedupe_rows(rows, SPONSOR_TRACKER_HEADERS)
        with tracker_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=SPONSOR_TRACKER_HEADERS)
            writer.writeheader()
            for row in normalized:
                writer.writerow({header: row.get(header, "") for header in SPONSOR_TRACKER_HEADERS})

    def _refresh_sponsors(self) -> None:
        try:
            rows = self._read_sponsor_rows()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Sponsor Tracker Error", str(exc))
            self.status_text.set("Unable to load sponsor tracker.")
            return

        for row_id in self.sponsor_table.get_children():
            self.sponsor_table.delete(row_id)

        ranked_rows = self._rank_sponsor_rows(rows)

        shown = 0
        for item in ranked_rows:
            row = item["row"]
            self.sponsor_table.insert(
                "",
                tk.END,
                values=(
                    row.get("Sponsor", ""),
                    item["vertical"],
                    row.get("Application Form URL", ""),
                    row.get("Program Type (Sponsorship/Affiliate/Both)", ""),
                    item["investment_raw"],
                    item["total_score"],
                    item["affordable_text"],
                    row.get("Status", ""),
                    row.get("Last Verified Date", ""),
                ),
            )
            shown += 1
        self.status_text.set(f"Loaded {shown} sponsor records (from {len(rows)} total).")

    def _rank_sponsor_rows(self, rows: list[dict[str, str]]) -> list[dict[str, object]]:
        budget = self._parse_float(self.sponsor_budget_var.get())
        affordable_only = self.sponsor_affordable_only_var.get()
        vertical_filter = self.sponsor_vertical_filter_var.get().strip()
        weights = self._score_weights()

        ranked_rows: list[dict[str, object]] = []
        for row in rows:
            vertical = row.get("Vertical", "").strip() or self._infer_vertical(row.get("Sponsor", ""))
            if vertical_filter and vertical_filter != "All" and vertical != vertical_filter:
                continue

            investment_raw = row.get("Estimated Investment Amount (USD)", "").strip()

            total_score, affordable_text = compute_total_score(row, budget=budget, weights=weights)

            is_affordable = affordable_text != "No"
            if affordable_text == "No":
                is_affordable = False
            elif affordable_text == "Yes":
                is_affordable = True

            if affordable_only and not is_affordable:
                continue

            ranked_rows.append(
                {
                    "row": row,
                    "vertical": vertical,
                    "investment_raw": investment_raw,
                    "affordable_text": affordable_text,
                    "total_score": total_score,
                }
            )

        ranked_rows.sort(key=lambda item: int(item["total_score"]), reverse=True)
        return ranked_rows

    def _auto_discover_sponsor_urls(self) -> None:
        rows = self._read_sponsor_rows()
        updated = 0
        for row in rows:
            if row.get("Application Form URL", "").strip() and row.get("Program/Partnership Page", "").strip():
                continue
            program_page, form_url, confidence = infer_program_urls(row.get("Website", ""))
            if program_page and not row.get("Program/Partnership Page", "").strip():
                row["Program/Partnership Page"] = program_page
                updated += 1
            if form_url and not row.get("Application Form URL", "").strip():
                row["Application Form URL"] = form_url
                updated += 1
            if confidence:
                note = row.get("Notes", "").strip()
                if confidence not in note:
                    row["Notes"] = (note + " | " if note else "") + confidence

        self._write_sponsor_rows(rows)
        self._refresh_sponsors()
        self.status_text.set(f"Auto-discovery updated {updated} URL fields.")

    def _export_weekly_sponsor_bundle(self) -> None:
        rows = self._read_sponsor_rows()
        ranked = self._rank_sponsor_rows(rows)
        top = ranked[:10]
        exports = self.paths.exports

        top_rows: list[dict[str, str]] = []
        for idx, item in enumerate(top, start=1):
            row = item["row"]
            top_rows.append(
                {
                    "Rank": str(idx),
                    "Sponsor": row.get("Sponsor", ""),
                    "Vertical": str(item["vertical"]),
                    "Total Score": str(item["total_score"]),
                    "Investment (USD)": str(item["investment_raw"]),
                    "Affordable": str(item["affordable_text"]),
                    "Status": row.get("Status", ""),
                }
            )
        write_csv(
            exports / "top_sponsors_this_week.csv",
            top_rows,
            ["Rank", "Sponsor", "Vertical", "Total Score", "Investment (USD)", "Affordable", "Status"],
        )

        followups = build_followup_rows(rows, base_date=date.today())
        write_csv(
            exports / "sponsor_followup_sequence.csv",
            followups,
            ["Sponsor", "Current Status", "Touchpoint", "Suggested Date", "Message Prompt"],
        )

        attribution_rows: list[dict[str, str]] = []
        for row in rows:
            sponsor = row.get("Sponsor", "")
            destination = row.get("Application Form URL", "").strip() or row.get("Website", "").strip()
            attribution_rows.append(
                {
                    "Sponsor": sponsor,
                    "Destination URL": destination,
                    "UTM URL": add_utm(destination, sponsor=sponsor),
                    "Coupon Placeholder": f"{normalize_sponsor_name(sponsor).upper().replace(' ', '')}-10",
                }
            )
        write_csv(
            exports / "sponsor_attribution_pack.csv",
            attribution_rows,
            ["Sponsor", "Destination URL", "UTM URL", "Coupon Placeholder"],
        )

        roi_rows = build_roi_rows(rows)
        write_csv(
            exports / "sponsor_roi_model.csv",
            roi_rows,
            [
                "Sponsor",
                "Estimated Investment (USD)",
                "Expected Conversions",
                "Commission per Conversion (USD)",
                "Expected Revenue (USD)",
                "Projected ROI (USD)",
                "Break-even Conversions",
            ],
        )

        write_kanban_markdown(exports / "sponsor_kanban_board.md", rows)

        dashboard_rows = build_dashboard_rows(rows)
        write_csv(
            exports / "sponsor_dashboard_summary.csv",
            dashboard_rows,
            ["Vertical", "Total Sponsors", "Lead", "Contacted", "Negotiating", "Active"],
        )

        self._refresh_outputs()
        self.status_text.set("Weekly sponsor bundle exported to data/exports.")

    def _save_sponsor_settings(self) -> None:
        budget = self.sponsor_budget_var.get().strip()
        parsed = self._parse_float(budget)
        if budget and parsed is None:
            messagebox.showerror("Invalid Budget", "Enter a valid numeric budget amount in USD.")
            return
        set_pref("sponsor_budget_usd", budget or "")
        set_pref("sponsor_affordable_only", bool(self.sponsor_affordable_only_var.get()))
        set_pref("sponsor_vertical_filter", self.sponsor_vertical_filter_var.get().strip() or "All")
        set_pref("sponsor_weight_fit", self.sponsor_weight_fit_var.get().strip() or "2")
        set_pref("sponsor_weight_readiness", self.sponsor_weight_readiness_var.get().strip() or "1")
        set_pref("sponsor_weight_access", self.sponsor_weight_access_var.get().strip() or "1")
        set_pref("sponsor_weight_budget", self.sponsor_weight_budget_var.get().strip() or "2")
        set_pref("sponsor_weight_form", self.sponsor_weight_form_var.get().strip() or "1")
        self._refresh_sponsors()
        self.status_text.set("Sponsor settings saved.")

    @staticmethod
    def _parse_int(raw: str, default: int = 0) -> int:
        try:
            return int((raw or "").strip())
        except ValueError:
            return default

    @staticmethod
    def _parse_float(raw: str) -> float | None:
        value = raw.strip().replace(",", "")
        if not value:
            return None
        try:
            return float(value)
        except ValueError:
            return None

    @staticmethod
    def _parse_score(raw: str) -> int:
        value = raw.strip()
        if not value:
            return 0
        try:
            parsed = int(value)
        except ValueError:
            return 0
        return max(0, min(parsed, 5))

    @staticmethod
    def _infer_vertical(sponsor_name: str) -> str:
        name = sponsor_name.lower()
        if any(token in name for token in ["audio", "pioneer", "kenwood", "kicker", "jl"]):
            return "Audio"
        if any(token in name for token in ["whaler", "marine", "donzi", "cigarette", "ski-doo", "polaris"]):
            return "Marine"
        if any(token in name for token in ["ducati", "ktm"]):
            return "Motorcycle"
        if any(token in name for token in ["snap", "blue-point", "fluke", "milwaukee", "tool"]):
            return "Tools"
        if any(token in name for token in ["aws", "google", "lenovo", "amazon"]):
            return "Computers/Cloud"
        if any(token in name for token in ["garmin", "flight", "industrial"]):
            return "Flight/Industrial"
        if any(token in name for token in ["black diamond", "carhartt", "outdoor", "colombia"]):
            return "Outdoor"
        if any(token in name for token in ["ford", "chevrolet", "mustang", "porsche", "subaru", "borla", "racing"]):
            return "Auto/Racing"
        return "Other"

    def _add_priority_sponsors(self) -> None:
        rows = self._read_sponsor_rows()
        existing = {row.get("Sponsor", "").strip().lower() for row in rows if row.get("Sponsor")}
        added = 0

        for seed in PRIORITY_SPONSORS:
            sponsor = seed.get("Sponsor", "").strip().lower()
            if not sponsor or sponsor in existing:
                continue

            row = {header: "" for header in SPONSOR_TRACKER_HEADERS}
            row.update(seed)
            row["Vertical"] = row.get("Vertical", "") or self._infer_vertical(row.get("Sponsor", ""))
            row["Fit Score (1-5)"] = row.get("Fit Score (1-5)", "") or "3"
            row["Readiness Score (1-5)"] = row.get("Readiness Score (1-5)", "") or "2"
            row["Access Score (1-5)"] = row.get("Access Score (1-5)", "") or "2"
            row["Last Verified Date"] = date.today().isoformat()
            rows.append(row)
            existing.add(sponsor)
            added += 1

        self._write_sponsor_rows(rows)
        self._refresh_sponsors()
        self.status_text.set(f"Added {added} priority sponsor targets.")

    def _add_sponsor_lead(self) -> None:
        sponsor_name = self.sponsor_name_entry.get().strip()
        if not sponsor_name:
            messagebox.showerror("Missing Sponsor", "Enter a sponsor name before adding a lead.")
            return

        normalized_name = normalize_sponsor_name(sponsor_name)

        rows = self._read_sponsor_rows()
        duplicate = any(normalize_sponsor_name(row.get("Sponsor", "")) == normalized_name for row in rows)
        if duplicate:
            messagebox.showerror("Duplicate Sponsor", "That sponsor already exists in the tracker.")
            return

        row = {header: "" for header in SPONSOR_TRACKER_HEADERS}
        row["Sponsor"] = normalized_name
        row["Website"] = self.sponsor_website_entry.get().strip()
        row["Vertical"] = self.sponsor_vertical_var.get().strip() or self._infer_vertical(sponsor_name)
        row["Application Form URL"] = self.sponsor_form_url_entry.get().strip()
        row["Application Method"] = self.sponsor_method_entry.get().strip() or "Researching"
        row["Estimated Investment Amount (USD)"] = self.sponsor_investment_entry.get().strip()
        row["Region Availability"] = self.sponsor_region_entry.get().strip()
        row["Fit Score (1-5)"] = self.sponsor_fit_entry.get().strip()
        row["Readiness Score (1-5)"] = self.sponsor_readiness_entry.get().strip()
        row["Access Score (1-5)"] = self.sponsor_access_entry.get().strip()
        row["Program Type (Sponsorship/Affiliate/Both)"] = "Both"
        row["Status"] = "Lead"
        row["Last Verified Date"] = date.today().isoformat()
        rows.append(row)

        self._write_sponsor_rows(rows)
        self._refresh_sponsors()

        self.sponsor_name_entry.delete(0, tk.END)
        self.sponsor_website_entry.delete(0, tk.END)
        self.sponsor_form_url_entry.delete(0, tk.END)
        self.sponsor_method_entry.delete(0, tk.END)
        self.sponsor_investment_entry.delete(0, tk.END)
        self.sponsor_region_entry.delete(0, tk.END)
        self.sponsor_fit_entry.delete(0, tk.END)
        self.sponsor_readiness_entry.delete(0, tk.END)
        self.sponsor_access_entry.delete(0, tk.END)
        self.status_text.set("Sponsor lead added.")


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    root = tk.Tk()
    MonetizeSocialGUI(root=root, project_root=project_root)
    root.mainloop()


if __name__ == "__main__":
    main()
