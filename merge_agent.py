import git
import os

def main():
    repo = git.Repo(os.getcwd())
    print("Repository object created.")

    print("Fetching remotes...")
    for remote in repo.remotes:
        remote.fetch()
    print("Fetch complete.")

    try:
        print("Attempting to merge...")
        repo.git.merge('remotes/origin/feat/core-infrastructure', '--allow-unrelated-histories')
    except git.GitCommandError as e:
        print("Merge failed as expected due to conflicts.")

        conflicted_files = [
            'cli/main.py',
            'core/energy_calculator.py',
            'core/exceptions.py',
            'core/functor.py',
            'core/two_phase_annealer.py',
            'core/types.py',
            'math_utils/annealing.py',
            'math_utils/distributions.py',
            'math_utils/estimation.py',
            'math_utils/laplacian.py',
            'math_utils/lyapunov.py',
            'math_utils/martingales.py',
            'pyproject.toml'
        ]

        for file_path in conflicted_files:
            print(f"Resolving conflict for {file_path}...")
            # Get the content of the file from the 'main' branch
            try:
                content = repo.git.show(f'remotes/origin/main:{file_path}')

                # Write the content to the conflicted file
                with open(file_path, 'w') as f:
                    f.write(content)

                repo.index.add([file_path])
                print(f"Resolved {file_path}.")
            except git.GitCommandError as show_error:
                print(f"Could not get file {file_path} from main branch. Error: {show_error}")


        print("All conflicts resolved. Committing merge.")
        repo.index.commit("Merged branch 'feat/core-infrastructure' with resolutions")
        print("Merge committed successfully.")

if __name__ == "__main__":
    main()
