"""
parse movie script to json
"""


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
            return prev_scene, name, None             # name line
        if line.startswith(self.dialog_ind):
            dialog = line.strip()
            if dialog is None or dialog == '' or dialog[0] == ' ':
                return None
            return prev_scene, prev_name, dialog      # dialog line
        for sind in self.scene_inds:
            if line.startswith(sind):
                return prev_scene + 1, None, None     # scene line
        return None


class ScriptParser:
    """movie script parser
    """
    def __init__(self,  name_ind: str ='                                 ',
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

    def parse(self, fsrc: str, fjson: str) -> Dict:
        """parse a movie script file

        Args:
            fsrc: input script filename
            fjson: output json filename
        
        Returns:
            A dict with keys `dialogs`, `scenes`, `all`
            `dialogs` : list of single_node_link_dict, of each line
            `scenes`: list of multi_node_link_dict, of each scene
            `all`: multi_node_link_dict, of the whole script
            single_node_link_dict = {`source`: src_id, `target`: dst_id, `dialog`: dialog}
            multi_node_link_dict = {`nodes`: a list of `node_dict`, `links`: a list of `link_dict`}
            `node_dict` = {`id`: node name, `group`: node degree}
            `link_dict` = {`source`: source node id, `target`: target node id, `value`: link weight,
                `dialogs`: list of dialogs (for `lines`, `dialogs` is a single dialog string)}
        """
        with open(fsrc, 'r') as f:
            lines = f.readlines()
        line_parser = LineParser(self.name_ind, self.dialog_ind, self.scene_inds)
        prev_scene = 0
        prev_name = None
        dialog_lines = list()       # for multi-line dialog merging
        triples = list()            # (scene, name, dialog) tuples of whole script
        for line in lines:
            try:
                scene_name_dialog = line_parser.parse(line, prev_scene, prev_name)
            except:
                continue
            if scene_name_dialog is None:           # empty/useless line
                continue
            if scene_name_dialog[1] is None:        # scene line
                if prev_name is not None and len(dialog_lines) > 0:
                    triples.append((prev_scene, prev_name, ' '.join(dialog_lines)))
                dialog_lines = list()
                prev_scene = scene_name_dialog[0]
            elif scene_name_dialog[2] is None:      # name line
                if prev_name is not None and len(dialog_lines) > 0:
                    triples.append((prev_scene, prev_name, ' '.join(dialog_lines)))
                dialog_lines = list()
                prev_name = scene_name_dialog[1]
            else:                                   # dialog line
                dialog_lines.append(scene_name_dialog[2])
        if prev_name is not None and len(dialog_lines) > 0:
            triples.append((prev_scene, prev_name, ' '.join(dialog_lines)))

        dialogs = list()                              # list of node_list_dict of each dialog
        prev_scene = 0
        pp_name = None
        prev_name = None
        prev_dialog = None
        scenes = list()                             # list of multi_node_link_dict of each scene
        node_dict = dict()                          # id (node name): group (node degree)
        link_dict = dict()                          # (source, target): list of dialogs, ensure source < target
        for triple in triples:
            scene = triple[0]
            name = triple[1]
            dialog = triple[2]
            if prev_name is not None:
                node_dict[prev_name] = node_dict.setdefault(prev_name, 0) + 1
            if scene == prev_scene:
                if prev_name is not None and name is not None and prev_name != name and prev_dialog is not None:
                    dialogs.append({'source': prev_name, 'target': name, 'dialog': prev_dialog})
                    link_tuple = (min(prev_name, name), max(prev_name, name))
                    link_dict.setdefault(link_tuple, []).append(prev_dialog)
            else:
                if pp_name is not None and prev_name is not None and pp_name != prev_name and prev_dialog is not None:
                    dialogs.append({'source': prev_name, 'target': pp_name, 'dialog': prev_dialog})
                    link_tuple = (min(prev_name, pp_name), max(prev_name, pp_name))
                    link_dict.setdefault(link_tuple, []).append(prev_dialog)
                prev_scene = scene
                scenes.append({'nodes': node_dict, 'links': link_dict})
                node_dict = dict()
                link_dict = dict()
            pp_name = prev_name
            prev_name = name
            prev_dialog = dialog
        if pp_name is not None and prev_name is not None and pp_name != prev_name and prev_dialog is not None:
            dialogs.append({'source': prev_name, 'target': pp_name, 'dialog': prev_dialog})
            link_tuple = (min(prev_name, pp_name), max(prev_name, pp_name))
            link_dict.setdefault(link_tuple, []).append(prev_dialog)
        scenes.append({'nodes': node_dict, 'links': link_dict})

        all = self._reduce_scenes(scenes)
        ret = {'dialogs': dialogs,
                'scenes': [self._to_json_form(scene['nodes'], scene['links']) for scene in scenes],
                'all': all}
        with open(fjson, 'w') as f:
            json.dump(ret, f, indent=4)
        return ret

    @staticmethod
    def _to_json_form(node_dict: Dict, edge_dict: Dict) -> Dict[str, List]:
        """
        Args:
            node_dict: {name: degree}
            edge_dict: {(source, target): list of dialogs}
        Returns:
            a json dict contains a node list and an edge list
            node list: [{"id": name, "group": degree}]
            edge list: [{"source": name, "target": name, "value": number of dialogs, "dialogs": list of dialogs}]
            refer to ../jsons/miserables.json
        """
        ret = {"nodes": [], "links": []}
        for name, val in node_dict.items():
            ret["nodes"].append({"id": name, "group": val})
        for src_tgt, val in edge_dict.items():
            ret["links"].append({"source": src_tgt[0], "target": src_tgt[1], "value": len(val), "dialogs": val})
        return ret

    @staticmethod
    def _reduce_scenes(scenes: List[Dict]) -> Dict[str, List]:
        """
        Args:
            scenes: list of {'nodes': list of {name: degree}, 'links': {(source, target): list of dialogs}}

        Returns:
            a json dict contains a node list and an edge list
            node list: [{"id": name, "group": degree}]
            edge list: [{"source": name, "target": name, "value": number of dialogs, "dialogs": list of dialogs}]
            refer to ../jsons/miserables.json
        """
        node_dict = dict()
        link_dict = dict()
        for scene in scenes:
            for name, val in scene['nodes'].items():
                node_dict[name] = node_dict.setdefault(name, 0) + val
            for src_tgt, val in scene['links'].items():
                link_dict.setdefault(src_tgt, []).extend(val)
        return ScriptParser._to_json_form(node_dict, link_dict)


if __name__ == '__main__':
    sp = ScriptParser()
    sp.parse('../movie_scripts/10tings.txt', '../jsons/10things_dialogs_scenes_all.json')
