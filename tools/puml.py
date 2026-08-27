import subprocess
from pathlib import Path

from plantuml import PlantUML


def group_classes_into_layers(lines: list[str]) -> list[str]:
    """Parses pyreverse PUML output and safely wraps classes into architectural packages."""
    layers = {
        "Control Plane (Orchestration)": [],
        "Business Logic (Application)": [],
        "Data Entities (Domain)": [],
        "Data Plane (Infrastructure)": [],
        "Shared Types & Configs": [],
    }
    relationships = []
    misc_lines = []

    current_layer = None
    current_block = []
    in_class_block = False

    for line in lines:
        stripped = line.strip()

        if not in_class_block:
            # 1. Identify the start of a class definition
            if (
                stripped.startswith("class ")
                or stripped.startswith("abstract ")
                or stripped.startswith("enum ")
                or stripped.startswith("interface ")
            ):
                in_class_block = True
                current_block = [line]

                # Map the class to a layer based on its module path
                if "vedika.orchestration" in line:
                    current_layer = "Control Plane (Orchestration)"
                elif "vedika.application" in line:
                    current_layer = "Business Logic (Application)"
                elif "vedika.domain" in line:
                    current_layer = "Data Entities (Domain)"
                elif "vedika.infrastructure" in line:
                    current_layer = "Data Plane (Infrastructure)"
                else:
                    current_layer = "Shared Types & Configs"

                # Handle 1-liner class declarations without curly braces
                if not stripped.endswith("{"):
                    in_class_block = False
                    layers[current_layer].extend(current_block)
                    current_block = []

            # 2. Capture relationship arrows
            elif any(
                arrow in stripped for arrow in ["<|--", "-->", "--|>", "*--", "o--", "..>", "<.."]
            ):
                relationships.append(line)

            # 3. Preserve essential configuration lines (e.g., set namespaceSeparator none)
            else:
                if stripped:
                    misc_lines.append(line)

        else:
            # Inside a class block
            current_block.append(line)
            if stripped == "}":
                in_class_block = False
                layers[current_layer].extend(current_block)
                current_block = []

    # 4. Reassemble the PUML file with package wrappers
    new_puml_lines = misc_lines[:]
    for layer_name, class_lines in layers.items():
        if class_lines:
            new_puml_lines.append(f'package "{layer_name}" {{\n')
            new_puml_lines.extend(class_lines)
            new_puml_lines.append("}\n\n")

    new_puml_lines.extend(relationships)
    return new_puml_lines


def build_layered_repo_diagram():
    docs_dir = Path("docs/architecture")
    docs_dir.mkdir(parents=True, exist_ok=True)

    print("1. Extracting the ENTIRE repository using pyreverse...")
    subprocess.run(
        ["pyreverse", "src/vedika", "-o", "puml", "-p", "Vedika", "-d", str(docs_dir)], check=True
    )

    puml_file = docs_dir / "classes_Vedika.puml"
    output_img = docs_dir / "vedika_layered_architecture.png"

    print("2. Grouping classes into architectural layers...")
    with open(puml_file, "r") as f:
        lines = f.readlines()

    # Extract standard styles
    custom_styles = [
        # "!theme blueprint\n",
        "skinparam shadowing false\n",
        "hide empty members\n",
        "left to right direction\n",
        "skinparam packageBackgroundColor #E8F4F8\n",
        "skinparam packageBorderColor #2980B9\n",
    ]

    start_idx = next(i for i, line in enumerate(lines) if "@startuml" in line)
    end_idx = next(i for i, line in enumerate(lines) if "@enduml" in line)

    core_content = lines[start_idx + 1 : end_idx]
    grouped_content = group_classes_into_layers(core_content)

    final_lines = ["@startuml\n"] + custom_styles + grouped_content + ["@enduml\n"]

    with open(puml_file, "w") as f:
        f.writelines(final_lines)

    print("3. Rendering the final layered PNG...")
    plantuml_client = PlantUML(url="http://www.plantuml.com/plantuml/png/")

    try:
        plantuml_client.processes_file(str(puml_file), outfile=str(output_img))
        print(f"Successfully generated layered UML text file at: {puml_file}")
        print(f"Successfully rendered layered PNG image at: {output_img}")
    except Exception:
        print("\n[Warning] The public PlantUML server rejected the request.")
        print(
            "This typically happens if the generated diagram is too large for the public web API."
        )
        print(f"Your .puml text file was successfully generated and saved to: {puml_file}")
        print("You can view it directly by installing the 'PlantUML' extension in VS Code.")


if __name__ == "__main__":
    build_layered_repo_diagram()


# import subprocess
# from pathlib import Path
#
# from plantuml import PlantUML
#
#
# def build_full_repo_diagram():
#     docs_dir = Path("docs/architecture")
#     docs_dir.mkdir(parents=True, exist_ok=True)
#
#     print("1. Extracting the ENTIRE repository using pyreverse...")
#     # pyreverse handles complex type hints and modern Python syntax without crashing
#     subprocess.run(
#         ["pyreverse", "src/vedika", "-o", "puml", "-p", "Vedika", "-d", str(docs_dir)], check=True
#     )
#
#     puml_file = docs_dir / "classes_Vedika.puml"
#     output_img = docs_dir / "vedika_full_architecture.png"
#
#     print("2. Injecting custom themes and aesthetics...")
#     with open(puml_file, "r") as f:
#         lines = f.readlines()
#
#     # Inject the global themes you previously customized
#     custom_styles = [
#         # "!theme blueprint\n",
#         "skinparam shadowing false\n",
#         "hide empty members\n",
#         "left to right direction\n",  # Spreads the massive diagram horizontally
#         "skinparam classBackgroundColor #F4F6F8\n",
#         "skinparam classBorderColor #2C3E50\n",
#     ]
#
#     for idx, line in enumerate(lines):
#         if "@startuml" in line:
#             lines = lines[: idx + 1] + custom_styles + lines[idx + 1 :]
#             break
#
#     with open(puml_file, "w") as f:
#         f.writelines(lines)
#
#     print("3. Rendering the final PNG (this may take a moment for the whole repo)...")
#     plantuml_client = PlantUML(url="http://www.plantuml.com/plantuml/png/")
#     plantuml_client.processes_file(str(puml_file), outfile=str(output_img))
#
#     print(f"Successfully generated full repo UML at {puml_file}")
#     print(f"Successfully rendered full repo PNG at {output_img}")
#
#
# if __name__ == "__main__":
#     build_full_repo_diagram()
#
#
# # import importlib
# # import inspect
# # import pkgutil
# # from pathlib import Path
# # from typing import get_type_hints
# #
# # from pdgen import generate_diagram, include_in_uml
# # from plantuml import PlantUML
# #
# # # Import the root of your package to begin scanning
# # import vedika
# #
# #
# # def discover_all_vedika_classes() -> list:
# #     """Scans the entire vedika package and returns a list of all defined classes."""
# #     discovered_classes = []
# #
# #     # Walk through all modules and submodules inside src/vedika
# #     for module_info in pkgutil.walk_packages(vedika.__path__, vedika.__name__ + "."):
# #         try:
# #             module = importlib.import_module(module_info.name)
# #             # Extract only the classes that are actually defined in this module (ignores external imports)
# #             for _, obj in inspect.getmembers(module, inspect.isclass):
# #                 if getattr(obj, "__module__", "") == module_info.name:
# #                     discovered_classes.append(obj)
# #         except Exception as e:
# #             print(f"Skipping module {module_info.name} during discovery: {e}")
# #
# #     return list(set(discovered_classes))
# #
# #
# # def generate_automated_arrows(target_classes: list) -> list[str]:
# #     """Introspects classes to auto-discover inheritance and dependencies."""
# #     arrows = []
# #     class_names = {c.__name__: c for c in target_classes}
# #
# #     for cls in target_classes:
# #         # 1. Auto-detect Inheritance
# #         for base in getattr(cls, "__bases__", []):
# #             if base.__name__ in class_names and base is not cls:
# #                 arrows.append(f"{base.__name__} <|-[#3498DB]- {cls.__name__} : inherits\n")
# #
# #         # 2. Auto-detect Dependencies via Method Type Hints
# #         for name, method in inspect.getmembers(cls, inspect.isfunction):
# #             try:
# #                 hints = get_type_hints(method)
# #                 for arg_name, hint_type in hints.items():
# #                     hint_str = str(hint_type)
# #
# #                     for target_name in class_names:
# #                         if target_name in hint_str and target_name != cls.__name__:
# #                             if arg_name == "return":
# #                                 arrows.append(
# #                                     f"{cls.__name__} -[#8E44AD]-> {target_name} : returns\n"
# #                                 )
# #                             else:
# #                                 arrows.append(
# #                                     f"{cls.__name__} .[#1ABC9C].> {target_name} : uses ({arg_name})\n"
# #                                 )
# #             except Exception:
# #                 pass
# #
# #     return list(set(arrows))
# #
# #
# # def build_architecture_diagrams():
# #     # 1. Dynamically discover EVERY class in the vedika repository
# #     target_classes = discover_all_vedika_classes()
# #     print(f"Discovered {len(target_classes)} classes in the vedika package.")
# #
# #     for cls in target_classes:
# #         include_in_uml(cls)
# #
# #     docs_dir = Path("docs/architecture")
# #     docs_dir.mkdir(parents=True, exist_ok=True)
# #
# #     puml_file = docs_dir / "automated_full_repo.puml"
# #     output_img = docs_dir / "automated_full_repo.png"
# #
# #     # 2. Generate the base boxes
# #     generate_diagram(output_img, puml_file)
# #
# #     with open(puml_file, "r") as f:
# #         lines = f.readlines()
# #
# #     # 3. Inject Global Themes
# #     custom_styles = [
# #         "!theme blueprint\n",
# #         "skinparam shadowing false\n",
# #         "hide empty members\n",
# #         "left to right direction\n",  # Added this to spread out large repo diagrams horizontally
# #     ]
# #
# #     for idx, line in enumerate(lines):
# #         if "@startuml" in line:
# #             lines = lines[: idx + 1] + custom_styles + lines[idx + 1 :]
# #             break
# #
# #     # 4. Inject the Auto-Discovered Arrows
# #     automated_arrows = generate_automated_arrows(target_classes)
# #
# #     for idx, line in enumerate(lines):
# #         if "@enduml" in line:
# #             lines = lines[:idx] + automated_arrows + lines[idx:]
# #             break
# #
# #     with open(puml_file, "w") as f:
# #         f.writelines(lines)
# #
# #     # 5. Render the final PNG
# #     plantuml_client = PlantUML(url="http://www.plantuml.com/plantuml/png/")
# #     plantuml_client.processes_file(str(puml_file), outfile=str(output_img))
# #
# #     print(f"Successfully generated full repo UML at {puml_file}")
# #
# #
# # if __name__ == "__main__":
# #     build_architecture_diagrams()
# #
# #
# # # import inspect
# # # from pathlib import Path
# # # from typing import get_type_hints
# # #
# # # from pdgen import generate_diagram, include_in_uml
# # # from plantuml import PlantUML
# # #
# # # from vedika.application.services.cleaning_service import CleaningService
# # # from vedika.domain.cleaned import BaseCleanedDomain
# # #
# # # # Import your pristine classes
# # # from vedika.domain.raw import BaseRawDomain, CodebaseRawDomain
# # #
# # #
# # # def generate_automated_arrows(target_classes: list) -> list[str]:
# # #     """Introspects classes to auto-discover inheritance and dependencies."""
# # #     arrows = []
# # #     class_names = {c.__name__: c for c in target_classes}
# # #
# # #     for cls in target_classes:
# # #         # 1. Auto-detect Inheritance
# # #         for base in getattr(cls, "__bases__", []):
# # #             if base.__name__ in class_names and base is not cls:
# # #                 arrows.append(f"{base.__name__} <|-[#3498DB]- {cls.__name__} : inherits\n")
# # #
# # #         # 2. Auto-detect Dependencies via Method Type Hints
# # #         for name, method in inspect.getmembers(cls, inspect.isfunction):
# # #             try:
# # #                 hints = get_type_hints(method)
# # #                 for arg_name, hint_type in hints.items():
# # #                     hint_str = str(hint_type)
# # #
# # #                     # Check if any target classes are mentioned in the type hint
# # #                     for target_name in class_names:
# # #                         if target_name in hint_str and target_name != cls.__name__:
# # #                             if arg_name == "return":
# # #                                 arrows.append(
# # #                                     f"{cls.__name__} -[#8E44AD]-> {target_name} : returns\n"
# # #                                 )
# # #                             else:
# # #                                 arrows.append(
# # #                                     f"{cls.__name__} .[#1ABC9C].> {target_name} : uses ({arg_name})\n"
# # #                                 )
# # #             except Exception:
# # #                 pass  # Skip methods with unresolvable type hints (e.g., missing imports)
# # #
# # #     return list(set(arrows))  # Deduplicate identical arrows
# # #
# # #
# # # def build_architecture_diagrams():
# # #     # 1. Define the exact classes you want mapped
# # #     target_classes = [BaseRawDomain, CodebaseRawDomain, BaseCleanedDomain, CleaningService]
# # #
# # #     for cls in target_classes:
# # #         include_in_uml(cls)
# # #
# # #     docs_dir = Path("docs/architecture")
# # #     docs_dir.mkdir(parents=True, exist_ok=True)
# # #
# # #     puml_file = docs_dir / "automated_connections.puml"
# # #     output_img = docs_dir / "automated_connections.png"
# # #
# # #     # 2. Let pdgen generate the base boxes
# # #     generate_diagram(output_img, puml_file)
# # #
# # #     with open(puml_file, "r") as f:
# # #         lines = f.readlines()
# # #
# # #     # 3. Inject Global Themes
# # #     custom_styles = ["!theme blueprint\n", "skinparam shadowing false\n", "hide empty members\n"]
# # #
# # #     for idx, line in enumerate(lines):
# # #         if "@startuml" in line:
# # #             lines = lines[: idx + 1] + custom_styles + lines[idx + 1 :]
# # #             break
# # #
# # #     # 4. Inject the Auto-Discovered Arrows
# # #     automated_arrows = generate_automated_arrows(target_classes)
# # #
# # #     for idx, line in enumerate(lines):
# # #         if "@enduml" in line:
# # #             lines = lines[:idx] + automated_arrows + lines[idx:]
# # #             break
# # #
# # #     with open(puml_file, "w") as f:
# # #         f.writelines(lines)
# # #
# # #     # 5. Render the final PNG
# # #     plantuml_client = PlantUML(url="http://www.plantuml.com/plantuml/png/")
# # #     plantuml_client.processes_file(str(puml_file), outfile=str(output_img))
# # #
# # #     print(f"Successfully generated automated UML at {puml_file}")
# # #
# # #
# # # if __name__ == "__main__":
# # #     build_architecture_diagrams()
# # #
# # #
# # # # import subprocess
# # # # from pathlib import Path
# # # #
# # # # from plantuml import PlantUML
# # # #
# # # #
# # # # def build_targeted_architecture_diagram():
# # # #     docs_dir = Path("docs/architecture")
# # # #     docs_dir.mkdir(parents=True, exist_ok=True)
# # # #
# # # #     # 1. Pass ONLY the specific files you want to map
# # # #     # This prevents the "spaghetti" diagram of the whole repo,
# # # #     # but still perfectly maps the relationships between these specific files.
# # # #     target_files = [
# # # #         "src/vedika/domain/raw.py",
# # # #         "src/vedika/domain/cleaned.py",
# # # #         "src/vedika/application/services/cleaning_service.py",
# # # #     ]
# # # #
# # # #     command = ["pyreverse", "-o", "puml", "-p", "Targeted", "-d", str(docs_dir)] + target_files
# # # #
# # # #     subprocess.run(command, check=True)
# # # #
# # # #     puml_file = docs_dir / "classes_Targeted.puml"
# # # #     output_img = docs_dir / "targeted_connections.png"
# # # #
# # # #     # 2. Render the PNG
# # # #     plantuml_client = PlantUML(url="http://www.plantuml.com/plantuml/png/")
# # # #     plantuml_client.processes_file(str(puml_file), outfile=str(output_img))
# # # #
# # # #     print(f"Successfully generated targeted UML at {puml_file}")
# # # #     print(f"Successfully rendered targeted PNG at {output_img}")
# # # #
# # # #
# # # # if __name__ == "__main__":
# # # #     build_targeted_architecture_diagram()
# # # #
# # # #
# # # # # from pathlib import Path
# # # # #
# # # # # from pdgen import generate_diagram, include_in_uml
# # # # # from plantuml import PlantUML
# # # # #
# # # # # from vedika.application.services.cleaning_service import CleaningService
# # # # # from vedika.domain.cleaned import BaseCleanedDomain
# # # # # from vedika.domain.raw import BaseRawDomain
# # # # #
# # # # #
# # # # # def build_architecture_diagrams():
# # # # #     include_in_uml(BaseRawDomain)
# # # # #     include_in_uml(BaseCleanedDomain)
# # # # #     include_in_uml(CleaningService)
# # # # #
# # # # #     docs_dir = Path("docs/architecture")
# # # # #     docs_dir.mkdir(parents=True, exist_ok=True)
# # # # #
# # # # #     puml_file = docs_dir / "domain_connections.puml"
# # # # #     output_img = docs_dir / "domain_connections.png"
# # # # #
# # # # #     # 1. Let pdgen generate the base .puml text file
# # # # #     generate_diagram(output_img, puml_file)
# # # # #
# # # # #     with open(puml_file, "r") as f:
# # # # #         lines = f.readlines()
# # # # #
# # # # #     # 2. Define global themes and colors (inserted at the top)
# # # # #     custom_styles = [
# # # # #         "!theme blueprint\n",  # Use a built-in PlantUML theme
# # # # #         "skinparam backgroundColor #FFFFFF\n",
# # # # #         "skinparam classBackgroundColor #F4F6F8\n",
# # # # #         "skinparam classBorderColor #2C3E50\n",
# # # # #         "skinparam classFontColor #1A1A1A\n",
# # # # #         "skinparam ArrowColor #E74C3C\n",  # Default color for all pdgen arrows
# # # # #         "skinparam shadowing false\n",
# # # # #         "hide empty members\n",  # Hides empty method/field boxes
# # # # #     ]
# # # # #
# # # # #     # 3. Define your custom arrows with inline specific colors (inserted at the bottom)
# # # # #     custom_arrows = [
# # # # #         "CleaningService .[#1ABC9C].> BaseRawDomain : uses\n",  # Teal dashed arrow
# # # # #         "CleaningService -[#8E44AD]-> BaseCleanedDomain : returns\n",  # Purple solid arrow
# # # # #         "BaseCleanedDomain -[#3498DB]-|> BaseRawDomain : inherits\n",  # Blue inheritance arrow
# # # # #     ]
# # # # #
# # # # #     # 4. Inject styles and arrows into the correct positions
# # # # #     for idx, line in enumerate(lines):
# # # # #         if "@startuml" in line:
# # # # #             lines = lines[: idx + 1] + custom_styles + lines[idx + 1 :]
# # # # #             break  # Stop after finding the start tag
# # # # #
# # # # #     # Re-evaluate lines length since we just added elements
# # # # #     for idx, line in enumerate(lines):
# # # # #         if "@enduml" in line:
# # # # #             lines = lines[:idx] + custom_arrows + lines[idx:]
# # # # #             break
# # # # #
# # # # #     with open(puml_file, "w") as f:
# # # # #         f.writelines(lines)
# # # # #
# # # # #     # 5. Re-render the PNG
# # # # #     plantuml_client = PlantUML(url="http://www.plantuml.com/plantuml/png/")
# # # # #     plantuml_client.processes_file(str(puml_file), outfile=str(output_img))
# # # # #
# # # # #     print(f"Successfully generated custom styled UML at {puml_file}")
# # # # #
# # # # #
# # # # # if __name__ == "__main__":
# # # # #     build_architecture_diagrams()
# # # # #
# # # # #
# # # # # # from pathlib import Path
# # # # # #
# # # # # # from pdgen import generate_diagram, include_in_uml
# # # # # # from plantuml import PlantUML
# # # # # #
# # # # # # from vedika.application.services.cleaning_service import CleaningService
# # # # # # from vedika.domain.cleaned import BaseCleanedDomain
# # # # # # from vedika.domain.raw import BaseRawDomain
# # # # # #
# # # # # #
# # # # # # def build_architecture_diagrams():
# # # # # #     # 1. Register the isolated classes
# # # # # #     include_in_uml(BaseRawDomain)
# # # # # #     include_in_uml(BaseCleanedDomain)
# # # # # #     include_in_uml(CleaningService)
# # # # # #
# # # # # #     docs_dir = Path("docs/architecture")
# # # # # #     docs_dir.mkdir(parents=True, exist_ok=True)
# # # # # #
# # # # # #     puml_file = docs_dir / "domain_connections.puml"
# # # # # #     output_img = docs_dir / "domain_connections.png"
# # # # # #
# # # # # #     # 2. Let pdgen generate the base .puml text file
# # # # # #     generate_diagram(output_img, puml_file)
# # # # # #
# # # # # #     # 3. Intercept the text file and explicitly add your arrows
# # # # # #     with open(puml_file, "r") as f:
# # # # # #         lines = f.readlines()
# # # # # #
# # # # # #     # Define your explicit PlantUML relationships here
# # # # # #     custom_arrows = [
# # # # # #         "CleaningService ..> BaseRawDomain : uses\n",
# # # # # #         "CleaningService --> BaseCleanedDomain : returns\n",
# # # # # #         "BaseCleanedDomain --|> BaseRawDomain : inherits (example)\n",
# # # # # #     ]
# # # # # #
# # # # # #     # Insert the arrows right before the @enduml tag
# # # # # #     for idx, line in enumerate(lines):
# # # # # #         if "@enduml" in line:
# # # # # #             lines = lines[:idx] + custom_arrows + lines[idx:]
# # # # # #             break
# # # # # #
# # # # # #     # Save the modified .puml file
# # # # # #     with open(puml_file, "w") as f:
# # # # # #         f.writelines(lines)
# # # # # #
# # # # # #     # 4. Re-render the PNG to include your new arrows
# # # # # #     plantuml_client = PlantUML(url="http://www.plantuml.com/plantuml/png/")
# # # # # #     plantuml_client.processes_file(str(puml_file), outfile=str(output_img))
# # # # # #
# # # # # #     print(f"Successfully generated custom UML at {puml_file}")
# # # # # #
# # # # # #
# # # # # # if __name__ == "__main__":
# # # # # #     build_architecture_diagrams()
# # # # # #
# # # # # #
# # # # # # # from pathlib import Path
# # # # # # #
# # # # # # # from pdgen import generate_diagram, include_in_uml
# # # # # # #
# # # # # # # from vedika.application.services.cleaning_service import CleaningService
# # # # # # # from vedika.domain.cleaned import BaseCleanedDomain
# # # # # # #
# # # # # # # # 1. Import the full hierarchy and dependencies
# # # # # # # from vedika.domain.raw import BaseRawDomain, CodebaseRawDomain
# # # # # # #
# # # # # # #
# # # # # # # def register_connected_classes():
# # # # # # #     """Registers classes in pairs/groups to ensure relationship arrows are drawn."""
# # # # # # #
# # # # # # #     # INHERITANCE MAP: Both parent and child must be registered
# # # # # # #     include_in_uml(BaseRawDomain)
# # # # # # #     include_in_uml(CodebaseRawDomain)  # pdgen will now draw an inheritance arrow
# # # # # # #
# # # # # # #     # COMPOSITION/DEPENDENCY MAP: Both the service and the types it uses
# # # # # # #     include_in_uml(BaseCleanedDomain)
# # # # # # #     include_in_uml(
# # # # # # #         CleaningService
# # # # # # #     )  # pdgen will draw an arrow if CleaningService type-hints BaseCleanedDomain
# # # # # # #
# # # # # # #
# # # # # # # def build_architecture_diagrams():
# # # # # # #     register_connected_classes()
# # # # # # #
# # # # # # #     output_img = Path("docs/architecture/domain_connections.png")
# # # # # # #     output_puml = Path("docs/architecture/domain_connections.puml")
# # # # # # #     output_img.parent.mkdir(parents=True, exist_ok=True)
# # # # # # #
# # # # # # #     generate_diagram(output_img, output_puml)
# # # # # # #     print(f"Successfully generated connected UML at {output_puml}")
# # # # # # #
# # # # # # #
# # # # # # # if __name__ == "__main__":
# # # # # # #     build_architecture_diagrams()
# # # # # # #
# # # # # # #
# # # # # # # ##
# # # # # # # # from pathlib import Path
# # # # # # # #
# # # # # # # # from pdgen import generate_diagram, include_in_uml
# # # # # # # #
# # # # # # # # from vedika.application.services.cleaning_service import CleaningService
# # # # # # # # from vedika.domain.cleaned import BaseCleanedDomain
# # # # # # # #
# # # # # # # # # 1. Import your pristine, untouched classes from the src/ folder
# # # # # # # # from vedika.domain.raw import BaseRawDomain, CodebaseRawDomain
# # # # # # # #
# # # # # # # #
# # # # # # # # def register_classes_for_uml():
# # # # # # # #     """Dynamically applies the pdgen decorator to imported classes."""
# # # # # # # #
# # # # # # # #     # Register core domain models
# # # # # # # #     include_in_uml(BaseRawDomain)
# # # # # # # #     include_in_uml(CodebaseRawDomain)
# # # # # # # #     include_in_uml(BaseCleanedDomain)
# # # # # # # #
# # # # # # # #     # Register services
# # # # # # # #     include_in_uml(CleaningService)
# # # # # # # #
# # # # # # # #     # You can even register specific methods if pdgen requires it
# # # # # # # #     # include_in_uml(CleaningService.clean_and_save_category)
# # # # # # # #
# # # # # # # #
# # # # # # # # def build_architecture_diagrams():
# # # # # # # #     # 2. Run the registration
# # # # # # # #     register_classes_for_uml()
# # # # # # # #
# # # # # # # #     # 3. Generate the outputs
# # # # # # # #     output_img = Path("docs/architecture/domain_models.png")
# # # # # # # #     output_puml = Path("docs/architecture/domain_models.puml")
# # # # # # # #
# # # # # # # #     generate_diagram(output_img, output_puml)
# # # # # # # #     print(f"Successfully generated UML at {output_puml}")
# # # # # # # #
# # # # # # # #
# # # # # # # # if __name__ == "__main__":
# # # # # # # #     build_architecture_diagrams()
# # # # # # #
# # # # # # #
# # # # # # # #
# # # # # # # # import subprocess
# # # # # # # # from pathlib import Path
# # # # # # # #
# # # # # # # # from plantuml import PlantUML
# # # # # # # #
# # # # # # # #
# # # # # # # # def build_full_architecture_diagram():
# # # # # # # #     docs_dir = Path("docs/architecture")
# # # # # # # #     docs_dir.mkdir(parents=True, exist_ok=True)
# # # # # # # #
# # # # # # # #     # 1. Extract the ENTIRE repository using pyreverse
# # # # # # # #     # Pointing it at "src/vedika" captures domain, application, infra, and orchestration
# # # # # # # #     subprocess.run(
# # # # # # # #         ["pyreverse", "src/vedika", "-o", "puml", "-p", "Vedika_Full", "-d", str(docs_dir)],
# # # # # # # #         check=True,
# # # # # # # #     )
# # # # # # # #
# # # # # # # #     # pyreverse automatically names the output file classes_{project_name}.puml
# # # # # # # #     puml_file = docs_dir / "classes_Vedika_Full.puml"
# # # # # # # #     output_img = docs_dir / "vedika_full_architecture.png"
# # # # # # # #
# # # # # # # #     # 2. Render the PNG using the official PlantUML client
# # # # # # # #     plantuml_client = PlantUML(url="http://www.plantuml.com/plantuml/png/")
# # # # # # # #     plantuml_client.processes_file(str(puml_file), outfile=str(output_img))
# # # # # # # #
# # # # # # # #     print(f"Successfully generated full repo UML at {puml_file}")
# # # # # # # #     print(f"Successfully rendered full repo PNG at {output_img}")
# # # # # # # #
# # # # # # # #
# # # # # # # # if __name__ == "__main__":
# # # # # # # #     build_full_architecture_diagram()
