import json
import os
import pytest
from datetime import datetime
from task_manager import (
    get_colored_status, check_file, crush_program, parse_input,
    add_task, delete_task, update_task, update_status,
    show_full_list, show_done_list, show_progress_list, show_todo_list, main,
    STATUS_COLORS, COLOR_RESET
)

TEST_FILENAME = "test_user_tasks.json"

def setup_function():
    with open(TEST_FILENAME, 'w') as file:
        json.dump({}, file)

def teardown_function():
    if os.path.exists(TEST_FILENAME):
        os.remove(TEST_FILENAME)

def test_add_task():
    add_task("Buy milk", filename=TEST_FILENAME)
    with open(TEST_FILENAME, 'r') as file:
        test_tasks_dict = json.load(file)
    assert len(test_tasks_dict) == 1
    task = test_tasks_dict["1"]
    assert task[0] == "Buy milk"
    assert task[1] == "todo"

def test_update_task():
    add_task("Buy milk", filename=TEST_FILENAME)
    update_task("1", "Updated task", filename=TEST_FILENAME)
    with open(TEST_FILENAME, 'r') as file:
        test_tasks_dict = json.load(file)
    assert test_tasks_dict["1"][0] == "Updated task"

def test_update_nonexistent_task():
    with pytest.raises(SystemExit) as excinfo:
        update_task("99", "Updated task", filename=TEST_FILENAME)
    assert "Error: You can't update this task because it's not on the to-do list." in str(excinfo.value)

def test_delete_task():
    add_task("Task to delete", filename=TEST_FILENAME)
    delete_task("1", filename=TEST_FILENAME)
    with open(TEST_FILENAME, 'r') as file:
        test_tasks_dict = json.load(file)
    assert test_tasks_dict == {}

def test_delete_nonexistent_task():
    with pytest.raises(SystemExit) as excinfo:
        delete_task("99", filename=TEST_FILENAME)
    assert "Error: You can't delete this task because it's not on the to-do list." in str(excinfo.value)

def test_update_status():
    add_task("Task to mark somehow", filename=TEST_FILENAME)
    update_status("1", "done", filename=TEST_FILENAME)
    with open(TEST_FILENAME, 'r') as file:
        test_tasks_dict = json.load(file)
    assert test_tasks_dict["1"][1] == "done"

def test_parse_input():
    assert parse_input("add Buy milk") == ["add", "Buy", "milk"]
    assert parse_input("delete 1") == ["delete", "1"]
    assert parse_input('add "Buy milk"') == ["add", "Buy milk"]

###################################################
# New unity tests
###################################################

def test_get_colored_status_known():
    status = "done"
    result = get_colored_status(status)
    assert STATUS_COLORS["done"] in result
    assert result.endswith(status + COLOR_RESET)

def test_get_colored_status_unknown():
    result = get_colored_status("invalid")
    assert "\033[37m" in result  # branco
    assert result.endswith("invalid" + COLOR_RESET)

def test_check_file_creates(tmp_path):
    file = tmp_path / "tasks.json"
    check_file(file)
    assert file.exists()

def test_check_file_already_exists(tmp_path):
    file = tmp_path / "tasks.json"
    file.write_text("{}")
    check_file(file)  # não deve lançar erro
    assert file.exists()


def test_crush_program_raises():
    with pytest.raises(SystemExit, match="Error: test reason"):
        crush_program("test reason")


def test_parse_input_without_quotes():
    s = "add tarefa simples"
    parts = parse_input(s)
    assert parts == ["add", "tarefa", "simples"]

def test_parse_input_with_quotes():
    s = 'add "tarefa com espacos"'
    parts = parse_input(s)
    assert parts == ["add", "tarefa com espacos"]


# ---------- TESTES DE OPERAÇÕES NO JSON ----------

def test_add_task_new_file(tmp_path):
    file = tmp_path / "tasks.json"
    file.write_text("")  # força JSONDecodeError
    add_task("Minha primeira tarefa", file)
    data = json.loads(file.read_text())
    assert 1 in map(int, data.keys())
    assert data["1"][0] == "Minha primeira tarefa"
    assert data["1"][1] == "todo"


def test_add_task_existing_file(tmp_path):
    file = tmp_path / "tasks.json"
    json.dump({"1": ["Task1", "todo", "2025-01-01", "N/A"]}, file.open("w"))
    add_task("Task2", file)
    data = json.load(file.open())
    assert len(data) == 2
    assert data["2"][0] == "Task2"


def test_delete_task_success(tmp_path):
    file = tmp_path / "tasks.json"
    json.dump({"1": ["Task1", "todo", "2025", "N/A"]}, file.open("w"))
    delete_task("1", file)
    data = json.load(file.open())
    assert data == {}


def test_delete_task_not_found(tmp_path):
    file = tmp_path / "tasks.json"
    json.dump({"1": ["Task1", "todo", "2025", "N/A"]}, file.open("w"))
    with pytest.raises(SystemExit, match="not on the to-do list"):
        delete_task("99", file)


def test_delete_task_empty_file(tmp_path):
    file = tmp_path / "tasks.json"
    file.write_text("")
    with pytest.raises(SystemExit, match="to-do list is empty"):
        delete_task("1", file)


def test_update_task_success(tmp_path):
    file = tmp_path / "tasks.json"
    json.dump({"1": ["Task1", "todo", "2025", "N/A"]}, file.open("w"))
    update_task("1", "Updated", file)
    data = json.load(file.open())
    assert data["1"][0] == "Updated"
    assert data["1"][2] == "2025"
    assert data["1"][3] != "N/A"


def test_update_task_not_found(tmp_path):
    file = tmp_path / "tasks.json"
    json.dump({}, file.open("w"))
    with pytest.raises(SystemExit, match="not on the to-do list"):
        update_task("2", "bla", file)


def test_update_task_empty_file(tmp_path):
    file = tmp_path / "tasks.json"
    file.write_text("")
    with pytest.raises(SystemExit, match="to-do list is empty"):
        update_task("1", "bla", file)


def test_update_status_success(tmp_path):
    file = tmp_path / "tasks.json"
    json.dump({"1": ["Task1", "todo", "2025", "N/A"]}, file.open("w"))
    update_status("1", "done", file)
    data = json.load(file.open())
    assert data["1"][1] == "done"


def test_update_status_not_found(tmp_path):
    file = tmp_path / "tasks.json"
    json.dump({"1": ["Task1", "todo", "2025", "N/A"]}, file.open("w"))
    with pytest.raises(SystemExit, match="not on the to-do list"):
        update_status("2", "done", file)


def test_update_status_empty_file(tmp_path):
    file = tmp_path / "tasks.json"
    file.write_text("")
    with pytest.raises(SystemExit, match="to-do list is empty"):
        update_status("1", "done", file)


# ---------- TESTES DE LISTAGEM ----------

@pytest.mark.parametrize("func, status", [
    (show_full_list, "todo"),
    (show_done_list, "done"),
    (show_progress_list, "in-progress"),
    (show_todo_list, "todo"),
])
def test_list_functions_prints(capsys, tmp_path, func, status):
    file = tmp_path / "tasks.json"
    json.dump({"1": ["Task1", status, "2025", "N/A"]}, file.open("w"))
    func(file)
    captured = capsys.readouterr()
    assert "Task1" in captured.out


@pytest.mark.parametrize("func", [show_full_list, show_done_list, show_progress_list, show_todo_list])
def test_list_functions_empty_file(tmp_path, func):
    file = tmp_path / "tasks.json"
    file.write_text("")
    with pytest.raises(SystemExit, match="empty now"):
        func(file)


@pytest.mark.parametrize("func, status", [
    (show_done_list, "todo"),
    (show_progress_list, "todo"),
    (show_todo_list, "done"),
])
def test_list_functions_nothing_to_display(capsys, tmp_path, func, status):
    file = tmp_path / "tasks.json"
    json.dump({"1": ["Task1", status, "2025", "N/A"]}, file.open("w"))
    func(file)
    captured = capsys.readouterr()
    assert "Nothing to display." in captured.out

# ---------- TESTES PARA main() ----------

def run_main_with_inputs(monkeypatch, inputs):
    """Executa main() com uma lista de inputs simulados."""
    it = iter(inputs)

    def fake_input(_):
        return next(it)

    monkeypatch.setattr("builtins.input", fake_input)
    main()


def test_main_exit_command(monkeypatch, capsys, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("task_manager.filename", str(tmp_path / "tasks.json"))

    run_main_with_inputs(monkeypatch, ["exit"])
    captured = capsys.readouterr()
    assert "Goodbye!" in captured.out


def test_main_quit_command(monkeypatch, capsys, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("task_manager.filename", str(tmp_path / "tasks.json"))

    run_main_with_inputs(monkeypatch, ["quit"])
    captured = capsys.readouterr()
    assert "Goodbye!" in captured.out


def test_main_help_command(monkeypatch, capsys, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("task_manager.filename", str(tmp_path / "tasks.json"))

    run_main_with_inputs(monkeypatch, ["help", "exit"])
    captured = capsys.readouterr()
    assert "Available commands:" in captured.out


def test_main_add_and_list(monkeypatch, capsys, tmp_path):
    file = tmp_path / "tasks.json"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("task_manager.filename", str(file))

    run_main_with_inputs(monkeypatch, ['add "Test task"', 'list all', 'exit'])
    captured = capsys.readouterr()
    assert "Test task" in captured.out
    assert "ID" in captured.out  # tabela exibida


def test_main_update_and_mark(monkeypatch, capsys, tmp_path):
    file = tmp_path / "tasks.json"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("task_manager.filename", str(file))

    # cria um ciclo com add -> update -> mark-done -> list done -> exit
    run_main_with_inputs(
        monkeypatch,
        ['add "Task1"', 'update 1 "Task1 updated"', 'mark-in-progress 1', 'mark-done 1', 'list done', 'exit']
    )
    captured = capsys.readouterr()
    assert "Task1 updated" in captured.out
    assert "done" in captured.out


def test_main_delete_command(monkeypatch, capsys, tmp_path):
    file = tmp_path / "tasks.json"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("task_manager.filename", str(file))

    run_main_with_inputs(
        monkeypatch,
        ['add "Task to delete"', 'delete 1', 'list all', 'exit']
    )
    captured = capsys.readouterr()
    assert "Nothing to display." in captured.out


@pytest.mark.parametrize("command", [
    "add",             # faltando descrição
    "delete",          # faltando id
    "update 1",        # faltando descrição
    "mark-done",       # faltando id
    "mark-in-progress",# faltando id
    "list invalid",    # filtro inválido
    "whatever"         # comando inexistente
])
def test_main_invalid_commands(monkeypatch, tmp_path, command):
    file = tmp_path / "tasks.json"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("task_manager.filename", str(file))

    try:
        run_main_with_inputs(monkeypatch, [command])
    except SystemExit:
        pass  # esperado
    except StopIteration:
        # também aceitável, significa que main pediu mais input
        pass
    else:
        pytest.fail("Esperava SystemExit ou StopIteration")


def test_main_keyboard_interrupt(monkeypatch, capsys, tmp_path):
    file = tmp_path / "tasks.json"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("task_manager.filename", str(file))

    # Simula um KeyboardInterrupt no primeiro input
    def fake_input(_):
        raise KeyboardInterrupt
    monkeypatch.setattr("builtins.input", fake_input)

    # Executa main() — não deve levantar exceção
    main()

    captured = capsys.readouterr()
    assert "Exiting Tasker." in captured.out