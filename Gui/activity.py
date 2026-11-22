
import customtkinter as ctk

from Core.activity import ActivityManager


class ActivityFrame(ctk.CTkFrame):

    def __init__(self, parent, user, on_back):
        super().__init__(
            parent,
            corner_radius=0,
            fg_color="#F4F6FA"
        )

        self.user = user
        self.on_back = on_back

        self.activity_manager = ActivityManager()

        self.build_interface()
        self.load_activities()

    def build_interface(self):

        header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        header.pack(
            fill="x",
            padx=35,
            pady=(30, 20)
        )

        ctk.CTkLabel(
            header,
            text="All Recent Activities",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#202938"
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="View your complete learning activity history.",
            font=ctk.CTkFont(size=14),
            text_color="#778195"
        ).pack(anchor="w", pady=(7, 15))

        ctk.CTkButton(
            header,
            text="Back to Dashboard",
            width=150,
            height=36,
            fg_color="#3157D5",
            hover_color="#2546B5",
            command=self.on_back
        ).pack(anchor="w", pady=(5, 0))

        self.activities_container = ctk.CTkScrollableFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=12,
            border_width=1,
            border_color="#E5E9F0"
        )

        self.activities_container.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=(0, 30)
        )

    def load_activities(self):

        for widget in self.activities_container.winfo_children():
            widget.destroy()

        activities = self.activity_manager.get_activities(
            self.user["email"]
        )

        if not activities:
            ctk.CTkLabel(
                self.activities_container,
                text="No activities recorded yet.",
                font=ctk.CTkFont(size=14),
                text_color="#8993A5"
            ).pack(pady=30)

            return

        for activity in activities:
            self.create_activity_item(activity)

    def create_activity_item(self, activity):

        item = ctk.CTkFrame(
            self.activities_container,
            fg_color="#F4F6FA",
            corner_radius=8
        )

        item.pack(
            fill="x",
            padx=12,
            pady=6
        )

        details = ctk.CTkFrame(
            item,
            fg_color="transparent"
        )

        details.pack(
            fill="x",
            padx=15,
            pady=12
        )

        ctk.CTkLabel(
            details,
            text=f"{activity['action']}: {activity['item_name']}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#202938"
        ).pack(anchor="w")

        if activity.get("details"):
            ctk.CTkLabel(
                details,
                text=activity["details"],
                font=ctk.CTkFont(size=12),
                text_color="#778195"
            ).pack(anchor="w", pady=(4, 0))

        ctk.CTkLabel(
            details,
            text=activity.get("created_at", ""),
            font=ctk.CTkFont(size=11),
            text_color="#8993A5"
        ).pack(anchor="w", pady=(4, 0))
