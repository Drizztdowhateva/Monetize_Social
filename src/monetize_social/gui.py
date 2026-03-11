from __future__ import annotations

import csv
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
from monetize_social.procedure import load_procedures


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
        self.outputs_tab = ttk.Frame(tabs, padding=10)

        tabs.add(self.procedure_tab, text="Procedure")
        tabs.add(self.pipeline_tab, text="Pipeline")
        tabs.add(self.campaign_tab, text="Hashtag Ads")
        tabs.add(self.outputs_tab, text="Outputs")

        self._build_procedure_layout()
        self._build_pipeline_layout()
        self._build_campaign_layout()
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

    def _load_procedure_tab(self) -> None:
        self.procedures = load_procedures(self.project_root)
        names = list(self.procedures.keys())

        self.procedure_selector["values"] = names
        if names:
            self.procedure_selector.current(0)
            self._render_procedure(names[0])

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
            self.project_root / "docs/onboarding_packets",
        ]

        for row_id in self.outputs_table.get_children():
            self.outputs_table.delete(row_id)

        for output in output_files:
            status = "Present" if output.exists() else "Missing"
            rel_path = output.relative_to(self.project_root)
            self.outputs_table.insert("", tk.END, values=(str(rel_path), status))


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    root = tk.Tk()
    MonetizeSocialGUI(root=root, project_root=project_root)
    root.mainloop()


if __name__ == "__main__":
    main()
