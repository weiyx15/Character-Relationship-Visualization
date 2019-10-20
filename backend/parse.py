import json
from typing import List, Dict, Tuple


class LineParser:
    """movie script line parser
    """
    def __init__(self,  name_ind: str ='                                 ',
                        dialog_ind: str ='                    ',
                        scene_inds: Tuple[str] =('          INT. ', )
                ):
        """
        Args:
            name_ind: indent before name in a name line
            dialog_ind: indent before dialog in a dialog line
            scene_inds: indent before scene in a scene line, variants exist
        """
        self.scene_inds = scene_inds
        self.name_ind = name_ind
        self.dialog_ind = dialog_ind

    def parse(self, line: str, prev_scene: int, prev_name: str) -> (int, str, str):
        """parse a line

        Args:
            line: a line of a movie script
        
        Returns:
            (scene, name, dialog) tuple
            if a scene line, name = None and dialog = None;
            if a name line, dialog = None;
            if a description line but not a scene line or an empty line,
             just returns None
        """
        if line is None or line == '':
            return None
        if line.startswith(self.name_ind):
            name = line.strip()
            if name is None or name == '' or name[0] == ' ':
                return None
            left_brac = name.find('(')
            if left_brac != -1:
                name = name[:left_brac-1]
            return (prev_scene, name, None)             # name line
        if line.startswith(self.dialog_ind):
            dialog = line.strip()
            if dialog is None or dialog == '' or dialog[0] == ' ':
                return None
            return (prev_scene, prev_name, dialog)      # dialog line
        for sind in self.scene_inds:
            if line.startswith(sind):
                return (prev_scene + 1, None, None)     # scene line
        return None


class ScriptParser:
    """movie script parser
    """
    def __init__(self,  fn: str,
                        name_ind: str ='                                 ',
                        dialog_ind: str ='                    ',
                        scene_inds: Tuple[str] =('          INT. ', )
                ):
        """
        Args:
            fn: file name to parse
            name_ind: indent before name in a name line
            dialog_ind: indent before dialog in a dialog line
            scene_inds: indent before scene in a scene line, variants exist
        """
        self.scene_inds = scene_inds
        self.name_ind = name_ind
        self.dialog_ind = dialog_ind
        self.triples = self.parse(fn)

    def parse(self, fn: str) -> List[Tuple]:
        """parse a movie script file

        Args:
            fn: filename
        
        Returns:
            a triple of (scene_id, name, joint_dialog)
        """
        with open(fn, 'r') as f:
            lines = f.readlines()
        line_parser = LineParser(self.name_ind, self.dialog_ind, self.scene_inds)
        prev_scene = 0
        prev_name = None
        dialog_lines = list()
        triples = list()
        for line in lines:
            try:
                scene_name_dialog = line_parser.parse(line, prev_scene, prev_name)
            except:
                continue
            if scene_name_dialog is None:           # empty/useline line
                continue
            if scene_name_dialog[1] == None:        # scene line
                if prev_name is not None and len(dialog_lines) > 0:
                    triples.append((prev_scene, prev_name, ' '.join(dialog_lines)))
                dialog_lines = list()
                prev_scene = scene_name_dialog[0]
            elif scene_name_dialog[2] == None:      # name line
                if prev_name is not None and len(dialog_lines) > 0:
                    triples.append((prev_scene, prev_name, ' '.join(dialog_lines)))
                dialog_lines = list()
                prev_name = scene_name_dialog[1]
            else:                                   # dialog line
                dialog_lines.append(scene_name_dialog[2])
        if prev_name is not None and len(dialog_lines) > 0:
            triples.append((prev_scene, prev_name, ' '.join(dialog_lines)))
        return triples

    @staticmethod
    def _to_json_form(node_dict: dict, edge_dict: dict) -> List[Dict]:
        """
        Args:
            node_dict: {"name": appearance times}
            edge_dict: {("source_name", "target_name"): appearance times}

        Returns:
            list of json dict ending on every scene
            a json dict contains a node list and an edge list
            node list: [{"id": name, "group": appearance times}]
            edge list: [{"source": name, "target": name, "value": appearance times}]
            refer to ../jsons/miserables.json
        """
        ret = {"nodes": [], "links": []}
        for name, val in node_dict.items():
            ret["nodes"].append({"id":name, "group": val})
        for src_tgt, val in edge_dict.items():
            ret["links"].append({"source": src_tgt[0], "target": src_tgt[1], "value":val})
        return ret

    def scene_json(self):
        """
        Returns:
            list of json dict ending on every scene
            a json dict contains a node list and an edge list
            node list: [{"id": name, "group": appearance times}]
            edge list: [{"source": name, "target": name, "value": appearance times}]
            refer to ../jsons/miserables.json
        """
        node_dict = dict()
        edge_dict = dict()
        prev_triple = (None, None, None)
        json_lst = list()
        for triple in self.triples:
            node_dict[triple[1]] = node_dict.setdefault(triple[1], 0) + 1
            if prev_triple[0] is not None:
                if triple[0] == prev_triple[0]:
                    edge_dict[(prev_triple[1], triple[1])] = \
                        edge_dict.setdefault((prev_triple[1], triple[1]), 0) + 1
                else:
                    json_lst.append(ScriptParser._to_json_form(node_dict, edge_dict))
            prev_triple = triple
        return json_lst


if __name__ == '__main__':
    sp = ScriptParser('../movie_scripts/10tings.txt')
    json_lst = sp.scene_json()
    with open('../jsons/10tings.json', 'w') as f:
        json.dump(json_lst[-1], f)