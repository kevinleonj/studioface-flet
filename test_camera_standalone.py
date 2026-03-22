"""Standalone camera test — minimal, no app dependencies."""

import flet as ft
import flet_camera as fc


def main(page: ft.Page):
    page.title = "Camera Test"
    page.bgcolor = "#131314"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20

    status = ft.Text("Status: waiting for Start Camera click", color="white", size=16)

    camera = fc.Camera(
        preview_enabled=True,
        expand=True,
    )

    camera_container = ft.Container(
        content=camera,
        width=400,
        height=300,
        bgcolor="#2A2A2B",
        border_radius=12,
    )

    def start_camera(e):
        async def do_start():
            status.value = "Making camera visible..."
            page.update()

            import asyncio
            await asyncio.sleep(1.0)

            status.value = "Getting cameras..."
            page.update()

            try:
                cameras = await camera.get_available_cameras()
                status.value = f"Found {len(cameras)} cameras"
                page.update()
                print(f"[TEST] Found {len(cameras)} cameras", flush=True)

                for i, c in enumerate(cameras):
                    print(f"[TEST]   [{i}] name={c.name} dir={c.lens_direction} lens={getattr(c, 'lens_type', '?')}", flush=True)

                if cameras:
                    front = [c for c in cameras if c.lens_direction == fc.CameraLensDirection.FRONT]
                    selected = front[0] if front else cameras[0]
                    print(f"[TEST] Initializing: {selected.name}", flush=True)
                    status.value = f"Initializing: {selected.name}..."
                    page.update()

                    await camera.initialize(
                        description=selected,
                        resolution_preset=fc.ResolutionPreset.HIGH,
                    )
                    status.value = f"Camera LIVE: {selected.name}"
                    page.update()
                    print("[TEST] Camera initialized OK", flush=True)
                else:
                    status.value = "No cameras found"
                    page.update()
            except Exception as ex:
                status.value = f"Error: {ex}"
                page.update()
                import traceback
                traceback.print_exc()

        page.run_task(do_start)

    def capture(e):
        async def do_capture():
            try:
                status.value = "Capturing..."
                page.update()
                img = await camera.take_picture()
                status.value = f"Captured: type={type(img).__name__} len={len(img) if img else 0}"
                page.update()
                print(f"[TEST] Captured: type={type(img).__name__} len={len(img) if img else 0}", flush=True)
            except Exception as ex:
                status.value = f"Capture error: {ex}"
                page.update()
                import traceback
                traceback.print_exc()

        page.run_task(do_capture)

    page.add(
        ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
            controls=[
                ft.Text("Camera Test", size=24, color="white",
                         weight=ft.FontWeight.BOLD),
                status,
                ft.Container(height=16),
                camera_container,
                ft.Container(height=16),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.ElevatedButton("Start Camera", on_click=start_camera,
                                          bgcolor="#F59E0B", color="#472A00"),
                        ft.ElevatedButton("Capture", on_click=capture,
                                          bgcolor="#F59E0B", color="#472A00"),
                    ],
                ),
            ],
        )
    )


ft.app(target=main)
