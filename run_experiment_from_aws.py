#!/usr/bin/env python

import os
import sys
import argparse
from slack_post import slack_post, slack_post_img
from os import path
from datetime import datetime
from subprocess import check_call


def main():
    local_sides = {
        'AWS Brazil': '52.67.203.197',
        'AWS California': '52.52.80.245',
        'AWS Korea': '52.79.43.78',
        'AWS India': '35.154.48.15',
    }

    remote_sides = {
        'Stanford': 'pi@171.66.3.65',
        'Brazil': 'pi@177.234.144.122',
        'Colombia': 'pi@138.121.201.58',
        'Mexico': 'pi@143.255.56.146',
        'China': 'yanyu@101.6.97.145',
        'Nepal': 'pi@nepal6',  # uses ssh alias, currently only AWS India works
        'India': 'pi@109.73.164.122',
    }

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'local', choices=local_sides.keys(), help='local side')
    parser.add_argument(
        'remote', choices=remote_sides.keys(), help='remote side')
    parser.add_argument(
        '--run-times', metavar='TIMES', action='store', dest='run_times',
        type=int, default=1, help='run times of each test')
    parser.add_argument(
        '--sender-side', choices=['local', 'remote'], action='store',
        dest='sender_side', default='remote',
        help='the side to be data sender (default remote)')
    parser.add_argument(
        '--remote-interface', metavar='INTERFACE', action='store',
        dest='remote_if', help='remote interface to run tunnel on')
    parser.add_argument(
        '--no-setup', action='store_true',
        help='skip running setup of schemes')
    parser.add_argument('--skip-analysis', action='store_true', help='skip running setup of schemes')
    args = parser.parse_args()


    if args.remote_if:
        remote_text = '%s %s' % (args.remote, args.remote_if)
    else:
        remote_text = args.remote

    if args.sender_side is 'remote':
        uploader = remote_text
        downloader = args.local
    else:
        uploader = args.local
        downloader = remote_text

    experiment_title = '%s to %s %d runs' % (uploader, downloader, args.run_times)

    slack_post('Running experiment uploading from ' + experiment_title + ".")

    test_dir = os.path.expanduser('~/pantheon/test/')
    os.chdir(test_dir)
    check_call('rm -rf *.log *.json *.png *.pdf *.out verus_tmp', shell=True)

    cmd = ('./run.py -r %s:~/pantheon -t 30 --tunnel-server local '
           '--local-addr %s --sender-side %s --local-info "%s" '
           '--remote-info "%s" --random-order --run-times %s'
           % (remote_sides[args.remote], local_sides[args.local],
              args.sender_side, args.local, args.remote, args.run_times))
    if args.remote_if:
        cmd += ' --remote-interface ' + args.remote_if

    if not args.no_setup:
        sys.stderr.write(cmd + ' --run-only setup\n')
        try:
            check_call(cmd + ' --run-only setup', shell=True)
        except:
            slack_post('Experiment uploading from ' + experiment_title + " failed during setup phase.")
            return

    sys.stderr.write(cmd + ' --run-only test\n')
    try:
        check_call(cmd + ' --run-only test', shell=True)
    except:
        experiment_title += ' FAILED'
        args.skip_analysis = False


    date = datetime.utcnow()
    date = date.replace(microsecond=0).isoformat().replace(':', '-')
    date = date[:-3]  # strip seconds

    experiment_file_prefix = '%s-%s' % (date, experiment_title.replace(' ', '-'))
    src_dir = '%s-logs' % experiment_file_prefix
    check_call(['mkdir', src_dir])
    check_call('mv *.log *.json ' + src_dir, shell=True)

    src_tar = src_dir + '.tar.xz'
    check_call('tar cJf ' + src_tar + ' ' + src_dir, shell=True)

    s3_base = 's3://stanford-pantheon/'
    s3_folder = 'real-world-results/%s/' % args.remote
    s3_url = s3_base + s3_folder + src_tar
    check_call('aws s3 cp ' + src_tar + ' ' + s3_url, shell=True)

    http_base = 'https://stanford-pantheon.s3.amazonaws.com/'
    http_url = http_base + s3_folder + src_tar
    slack_text = ("Logs archive of %s uploaded to:\n<%s>\n"
                  "To generate report run:\n`pantheon/analyze/analyze.py "
                  "--s3-link %s`" % (experiment_title, http_url, http_url))
    slack_post(slack_text)

    sys.stderr.write('Logs archive uploaded to: %s\n' % http_url)

    if not args.skip_analysis:
        cmd = ('../analyze/analyze.py --data-dir ../test/%s' % src_dir)
        check_call(cmd, shell=True)

        local_pdf = '%s/pantheon_report.pdf' % src_dir
        s3_analysis_folder = s3_folder + 'reports/'
        s3_pdf = experiment_file_prefix + '_report.pdf'
        s3_url = s3_base + s3_analysis_folder + s3_pdf
        check_call(['aws', 's3', 'cp', local_pdf, s3_url])

        http_url = http_base + s3_analysis_folder + s3_pdf
        slack_text = "Analysis of %s uploaded to:\n<%s>\n" % (experiment_title, http_url)
        slack_post(slack_text)

        imgs_to_upload = ['pantheon_summary.png'] 
        # Don't post summary means chart if there is only one run
        if args.run_times > 1:
            imgs_to_upload.append('pantheon_summary_mean.png')

        for img in imgs_to_upload:
            local_img = '%s/%s' % (src_dir, img)
            s3_img = experiment_file_prefix + '_' + img
            s3_url = s3_base + s3_analysis_folder + s3_img
            check_call(['aws', 's3', 'cp', local_img, s3_url])
            img_title = '%s from %s' % (img, experiment_title)
            http_url = http_base + s3_analysis_folder + s3_img
            slack_post_img(img_title, http_url)

    check_call(['rm', '-rf', src_dir, src_tar])


if __name__ == '__main__':
    main()
